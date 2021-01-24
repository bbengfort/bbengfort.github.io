---
categories: snippets
date: "2017-09-28T10:44:30Z"
title: Lock Diagnostics in Go
---

By now it's pretty clear that I've just had a bear of a time with locks and synchronization inside of multi-threaded environments with Go. Probably most gophers would simply tell me that I should share memory by communicating rather than to communication by sharing memory &mdash; and frankly I'm in that camp too. The issue is that:

- Mutexes can be more expressive than channels
- Channels are fairly heavyweight

So to be honest, there are situations where a mutex is a better choice than a channel. I believe that one of those situations is when dealing with replicated state machines &hellip; which is what I've been working on the past few months. The issue is that the state of the replica has to be consistent across a variety of events: timers and remote messages. The problem is that the timers and network traffic are all go routines, and there can be a lot of them running in the system at a time.

Of course you could simply create a channel and push event objects to it to serialize all events. The problem with that is that events generate other events that have to be ordered with respect to the parent event. For example, one event might require the generation of messages to be sent to remote replicas, which requires a per-remote state read that is variable. Said another way, the state can be read locked for all go routines operating at that time, but no write locks can be acquired. Hence the last post.

Things got complicated. Lock contention was a thing.

So I had to diagnose who was trying to acquire locks and when and why they were contending. For reference, the most common issues were:

1. A global read lock was being released before all sub read locks were finished.
2. A struct with an embedded `RWMutex` was then embedded by another object with only a `Mutex` but it still had `RLock()` methods as a result (or vice versa).
3. The wrong lock was being called on embedded structs.

The primary lesson I learned was this: _when embedding synchronized objects, only embed the mutex on the child object_. Hopefully that rule of thumb lasts.

I learned these lessons using a handy little diagnostic tool that this snippet is about. Basically I wanted to track who was acquiring locks and who was waiting on locks. I could then print out a report when I thought something was contending (e.g. on an `Interrupt` signal) and figure things out.

First step, figure out the name of the calling method:

```go
// Caller returns the name function that called the function which
// called the caller function.
func caller() string {
	pc, _, _, ok := runtime.Caller(2)
	details := runtime.FuncForPC(pc)
	if ok && details != nil {
		return details.Name()
	}
	return UnknownCaller
}
```

This handy little snippet uses the `runtime` package to detect the caller two steps above the `caller()` function in the stack. This allows you to call `caller()` inside of a function to get the name of the function that's calling the function calling `caller()`. Confusing? Try this:

```go
func outer() string {
    return inner()
}

func inner() string {
    return caller()
}
```

Calling `outer()` will return something like `main.outer` &mdash; the function that called the `inner()` function. Here is a [runnable example](https://play.golang.org/p/f8LJl3LErR).

With that in hand we can simply create a `map[string]int64` and increment any calls by caller name before `Lock()` and decrement any calls by caller name after `Unlock()`. Here is the example:

<script src="https://gist.github.com/bbengfort/9388bd2806d3692baeb8c5c2749cc739.js"></script>

But &hellip; that's actually a little more complicated than I let on!

The problem is that we definitely have multiple go routines calling locks on the lockable struct. However, if we simply try to access the `map` in the `MutexD`, then we can have a panic for concurrent map reads and writes. So now, I use the share memory by communicating technique and pass signals via an internal channel, which is read by a go routine ranging over it.

How to use it? Well do something like this:

```go
type StateMachine struct {
    MutexD
}

func (s *StateMachine) Alpha() {
    s.Lock()
    defer s.Unlock()
    time.Sleep(1*time.Second)
}

func (s *StateMachine) Bravo() {
    s.Lock()
    defer s.Unlock()
    time.Sleep(100*time.Millisecond)
}

func main() {
    m := new(StateMachine)
    go m.Alpha()
    time.Sleep(100*time.Millisecond)
    for i:=0; i < 2; i++ {
        go m.Bravo()
    }

    fmt.Println(m.MutexD.String())
}
```

You should see something like:

```
1 locks requested by main.(*StateMachine).Alpha
2 locks requested by main.(*StateMachine).Bravo
```

Obviously you can do the same thing for `RWMutex` objects, and it's easy to swap them in and out of code by changing the package and adding or removing a "D". My implementation is here: [github.com/bbengfort/x/lock](https://godoc.org/github.com/bbengfort/x/lock).
