---
categories: snippets
date: "2017-02-21T10:48:24Z"
title: Synchronizing Structs for Safe Concurrency in Go
---

Go is [built for concurrency](https://divan.github.io/posts/go_concurrency_visualize/) by providing language features that allow developers to embed complex concurrency patterns into their applications. These language features can be intuitive and a lot of safety is built in (for example a [race detector](https://blog.golang.org/race-detector)) but developers still need to be aware of the interactions between various threads in their programs.

In any shared memory system the biggest concern is [synchronization](https://en.wikipedia.org/wiki/Synchronization_(computer_science)): ensuring that separate go routines operate in the correct order and that no race conditions occur. The primary way to handle synchronization is the use of [channels](https://gobyexample.com/channels). Channels synchronize execution by forcing sends on the channel to block until the value on the channel is received. In this way, channels act as a [barrier](https://en.wikipedia.org/wiki/Barrier_(computer_science)) since the go routine can not progress while being blocked by the channel and enforce a specific ordering to execution, the ordering of routines arriving at the barrier.

Channels are made to implement [CSP](https://en.wikipedia.org/wiki/Communicating_sequential_processes), but there are other concurrency primitives like [mutexes](https://en.wikipedia.org/wiki/Lock_(computer_science)) (locks designed to enforce mutual exclusion concurrency control). In fact, channels use locks behind the scenes to serialize access, and [you're likely going to have to use other concurrency primitives anyway](http://www.jtolds.com/writing/2016/03/go-channels-are-bad-and-you-should-feel-bad/). I've encountered this problem, and have started using mutexes in a very specific way, which this post is about.

Consider an operation that is not [commutative](https://en.wikipedia.org/wiki/Commutative_property) or not [associative](https://en.wikipedia.org/wiki/Associative_property) (operations that are can be implemented with [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)), for example concatenating data to a buffer. This operation must be synchronized because the original state must be preserved during the operation. A simple explanation of this is the `+=` which (for the purpose of our discussion) fetches the original value of the variable, performs the operation and stores the result back to the value. If two processes attempt to `+=` concurrently a [race condition](https://en.wikipedia.org/wiki/Race_condition) occurs because whichever process is first to complete will have its answer overridden. In the following example, the final result of the variable will be `"hello Bob"` or `"hello Alice"` depending on which process gets there last, an undesirable state (the second operation may have preferred the concatenation to be `"hello Bob and Alice"` or `"hello Alice and Bob"`).

[![Race Condition]({{site.base_url }}/assets/images/2017-02-21-race-condition.png)]({{site.base_url }}/assets/images/2017-02-21-race-condition.png)

The solution is to lock the variable whenever the first process accesses it and then release it when it's done, that way the process is guaranteed the state of the variable for the duration of the operation. Here's how I implement this with a `struct` in Go:

```go
type Buffer struct {
    sync.Mutex        // wraps a synchronization flag
    buf        string // the string being concatenated to
}
```

By embedding the `sync.Mutex` into the struct, it can now be locked and unlocked. Even more powerfully, you can write methods that lock and `defer` unlock for very easy thread safe synchronization. Here is an example of safe and unsafe concatenation to the buffer:

```go
func (b *Buffer) Concat(s string) {
	b.buf += s
}

func (b *Buffer) SafeConcat(s string) {
	b.Lock()
	defer b.Unlock()
	b.Concat(s)
}
```

It is important to note that safety does not mean that you're guaranteed some other arbitrary order of operations when using goroutines. Consider the following concurrent concatenate example that injects some sleep into the concat function (find the [complete code on Gist](https://gist.github.com/bbengfort/dcd6a1a36a9670562fe8a04cf836ce49)):

```go
var (
	safe   bool
	start  time.Time
	group  *sync.WaitGroup
	buffer *Buffer
	alphas []string
)

func write(idx int, safe bool) {
	defer group.Done()

	if idx >= len(alphas) {
		return
	}

	if safe {
		buffer.SafeConcat(alphas[idx])
	} else {
		buffer.Concat(alphas[idx])
	}

}

group = new(sync.WaitGroup)
alphas = []string{"a", "b", "c", "d", "e", "f", "g", "h", "i",}
buffer = new(Buffer)
start = time.Now()

for i := 0; i < len(alphas); i++ {
    group.Add(1)
    go write(i, safe)
}

group.Wait()
fmt.Printf("\nresult: %s in %s (safe=%t)\n", buffer, time.Since(start), safe)
```

Here, we're using a `sync.WaitGroup` to determine when all the go routines are complete (e.g. join on the collection of routines) and have them write the letter of their index to the buffer. The output is as follows:

```
result: fiedhcjgab in 1.004835942s (safe=false)
result: kbahgifjced in 11.020241668s (safe=true)
```

Note that in the unsafe case, one of the letters is missing because of incorrect synchronization and that the safe case took 11 seconds to complete. This is because each goroutine had to wait (for a second) until it could access the buffer since it was locked. However, it's also important to note that neither method (safe or unsafe) produced `"abcdefghijk"`, since the locking order is about which routine got to the lock first, not about what order the goroutine was started.

And honestly, that's the prime lesson from this post (most of which are my notes from implementing this in a production system).

But of course, I have another question - given the sequential case, how much overhead do the locks add? So benchmarking ...

```
BenchmarkUnsafeConcat-8   	 1000000	     47287 ns/op
BenchmarkSafeConcat-8     	 1000000	     53170 ns/op
```

Clearly having locks adds some overhead and if you're not going to do any concurrent programming, then the 6 microseconds it takes to lock and unlock is probably not worth it. On the other hand, if there is the chance that you'll have any concurrency at all - using the `sync.Mutex` embedding is a very clear and understandable way to go about things. 
