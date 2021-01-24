---
aliases:
- /snippets/2017/09/08/lock-queueing.html
categories: snippets
date: '2017-09-08T11:31:19Z'
draft: false
showtoc: false
slug: lock-queueing
title: Lock Queuing in Go
---

In Go, you can use `sync.Mutex` and `sync.RWMutex` objects to create thread-safe data structures in memory as discussed in [&ldquo;Synchronizing Structs for Safe Concurrency in Go&rdquo;]({% post_url 2017-02-21-synchronizing-structs %}). When using the `sync.RWMutex` in Go, there are two kinds of locks: read locks and write locks. The basic difference is that many read locks can be acquired at the same time, but only one write lock can be acquired at at time.

This means that if a thread attempts to acquire a read lock on an object that is already read locked, then it will not block and it will acquire its own read lock. If a thread attempts to acquire a read or a write lock on a write locked object, then it will block until it is unlocked (as will a write lock acquisition on a read locked object).

Granting a lock can be prioritized depending on different [policies for accesses](https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock). Priorities balance the trade-off between concurrency and starvation as follows:

1. _Read-Preferring RW_ allows new read locks to be acquired as long as the lock is read-locked, forcing the write-lock acquirer to wait until there are no more read-locks. In high contention environments, this might lead to write-starvation.

2. _Write-Preferring RW_ prevents a read-lock acquisition if a writer is queued and waiting for the lock. This reduces concurrency, because new read locks have to wait for the write lock, but prevents starvation.

So which of these does Go implement? According to the documentation:

> If a goroutine holds a RWMutex for reading and another goroutine might call Lock, no goroutine should expect to be able to acquire a read lock until the initial read lock is released. In particular, this prohibits recursive read locking. This is to ensure that the lock eventually becomes available; a blocked Lock call excludes new readers from acquiring the lock. [&mdash; godoc](https://golang.org/pkg/sync/#RWMutex)

My initial read of this made me think  that Go implements write-preferring mutexes. However, this was not the behavior that I observed.

Consider the following locker:

```go
var delay time.Duration
var started time.Time

// Locker holds values that are threadsafe
type Locker struct {
	sync.RWMutex
	value  uint64    // the current value of the locker
	access time.Time // time of the last access
}

// Write to the value of the locker in a threadsafe fashion.
func (l *Locker) Write(value uint64) {
	l.Lock()
	defer l.Unlock()

	// Arbitrary amount of work
	time.Sleep(delay)

	l.value = value
	l.access = time.Now()
	l.log("written")
}

// Read the value of the locker in a threadsafe fasion.
func (l *Locker) Read() uint64 {
	l.RLock()
	defer l.RUnlock()

	// Arbirtray amount of work
	time.Sleep(delay / 2)
	l.access = time.Now()
	l.log("read")
	return l.value
}

// Log the access (not thread-safe)
func (l *Locker) log(method string) {
	after := l.access.Sub(started)
	log.Printf(
		"%d %s after %s\n", l.value, method, after,
	)
}
```

This locker holds a value and logs all accesses to it after the start time. If we run a few threads to read and write to it we can see concurrent reads in action:

```go
func main() {
	delay = 1 * time.Second
	started = time.Now()
	group := new(errgroup.Group)
	locker := new(Locker)

	// Straight forward, write three reads and a write
	group.Go(func() error { locker.Write(42); return nil })
	group.Go(func() error { locker.Read(); return nil })
	group.Go(func() error { locker.Read(); return nil })
	group.Go(func() error { locker.Read(); return nil })
	group.Go(func() error { locker.Write(101); return nil })

	group.Wait()
}
```

The output is as follows

```text
$ go run locker.go
2017/09/08 12:26:32 101 written after 1.005058824s
2017/09/08 12:26:33 101 read after 1.50770225s
2017/09/08 12:26:33 101 read after 1.507769109s
2017/09/08 12:26:33 101 read after 1.50773587s
2017/09/08 12:26:34 42 written after 2.511968581s
```

Note that the last go routine actually managed to acquire the lock first, after which the three readers managed to acquire the lock, then finally the last writer. Now if we interleave the read and write access, adding a sleep between the kick-off of each go routine to ensure that the preceding thread has time to acquire the lock:

```go
func main() {
	delay = 1 * time.Second
	started = time.Now()
	group := new(errgroup.Group)
	locker := new(Locker)

	// Straight forward, write three reads and a write
	group.Go(func() error { locker.Write(42); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Read(); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Write(101); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Read(); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Write(3); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Read(); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Write(18); return nil })
	time.Sleep(10 * time.Millisecond)
	group.Go(func() error { locker.Read(); return nil })

	group.Wait()
}
```

We get the following output:

```text
go run locker.go
2017/09/08 12:29:28 42 written after 1.000178155s
2017/09/08 12:29:28 42 read after 1.500703007s
2017/09/08 12:29:28 42 read after 1.500691088s
2017/09/08 12:29:28 42 read after 1.500756144s
2017/09/08 12:29:28 42 read after 1.500648159s
2017/09/08 12:29:28 42 read after 1.500762323s
2017/09/08 12:29:28 42 read after 1.500679533s
2017/09/08 12:29:28 42 read after 1.500795204s
2017/09/08 12:29:29 101 written after 2.500971593s
2017/09/08 12:29:30 3 written after 3.505325487s
2017/09/08 12:29:31 18 written after 4.50594131s
```

This suggests that the reads continue to acquire locks as long as the `Locker` is read locked, forcing the writes to happen at the end.

I found one Stack Overflow post: [&ldquo;Read preferring RW mutex lock in Golang&rdquo;](https://stackoverflow.com/questions/36548702/read-preferring-rw-mutex-lock-in-golang) that seems to suggest that `sync.RWMutex` can implement both read and write preferred locking, but doesn't really give an explanation about how external callers can implement it.

Finally consider the following:

```go
func main() {
	delay = 1 * time.Second
	started = time.Now()
	group := new(errgroup.Group)
	locker := new(Locker)

	// Straight forward, write three reads and a write
	group.Go(func() error { locker.Write(42); return nil })
	group.Go(func() error { locker.Write(101); return nil })
	group.Go(func() error { locker.Write(3); return nil })
	group.Go(func() error { locker.Write(18); return nil })

	for i := 0; i < 22; i++ {
		group.Go(func() error {
			locker.Read()
			return nil
		})
		time.Sleep(delay / 4)
	}

	group.Wait()
}
```

Given the loop issuing 22 read locks that sleep only a quarter of the time of the write lock, we might expect that this code will issue 22 read locks then all the write locks will occur at the end (and if we put this in a forever loop, then the writes would never occur). However, the output of this is as follows:

```text
2017/09/08 12:43:40 18 written after 1.004461829s
2017/09/08 12:43:40 18 read after 1.508343716s
2017/09/08 12:43:40 18 read after 1.50842899s
2017/09/08 12:43:40 18 read after 1.508362345s
2017/09/08 12:43:40 18 read after 1.508339659s
2017/09/08 12:43:40 18 read after 1.50852229s
2017/09/08 12:43:41 42 written after 2.513789339s
2017/09/08 12:43:42 42 read after 3.0163191s
2017/09/08 12:43:42 42 read after 3.016330534s
2017/09/08 12:43:42 42 read after 3.016355628s
2017/09/08 12:43:42 42 read after 3.016371381s
2017/09/08 12:43:42 42 read after 3.016316992s
2017/09/08 12:43:43 3 written after 4.017954589s
2017/09/08 12:43:43 3 read after 4.518495233s
2017/09/08 12:43:43 3 read after 4.518523255s
2017/09/08 12:43:43 3 read after 4.518537387s
2017/09/08 12:43:43 3 read after 4.518540397s
2017/09/08 12:43:43 3 read after 4.518543262s
2017/09/08 12:43:43 3 read after 4.51863128s
2017/09/08 12:43:44 101 written after 5.521872765s
2017/09/08 12:43:45 101 read after 6.023207828s
2017/09/08 12:43:45 101 read after 6.023225272s
2017/09/08 12:43:45 101 read after 6.023249529s
2017/09/08 12:43:45 101 read after 6.023190828s
2017/09/08 12:43:45 101 read after 6.023243032s
2017/09/08 12:43:45 101 read after 6.023190457s
2017/09/08 12:43:45 101 read after 6.04455716s
2017/09/08 12:43:45 101 read after 6.29457923s
```

What Go implements is actually something else: read locks can only be acquired _so long as the original read lock is maintained_ (the word &ldquo;initial&rdquo; being critical in the documentation). As soon as the first read lock is released, then the queued write-lock gets priority. The first read lock lasts approximately 500ms; this means that there is enough time for between 4-5 other locks to acquire a read lock, as soon as the first read lock completes, the write is given priority.
