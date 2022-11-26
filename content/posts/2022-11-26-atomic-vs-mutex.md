---
title: "Atomic vs Mutex"
slug: "atomic-vs-mutex"
date: "2022-11-26T12:24:25-06:00"
draft: false
categories: snippets
showtoc: false
---

When implementing Go code, I find myself chasing increased concurrency performance by trying to reduce the number of locks in my code. Often I wonder if using the `sync/atomic` package is a better choice because I know (as proved by this blog post) that atomics have far more performance than mutexes. The issue is that reading on the internet, including the [package documentation](https://pkg.go.dev/sync/atomic) itself strongly recommends relying on channels, then mutexes, and finally atomics _only if you know what you're doing_.

The primary difference is that the `sync/atomic` package uses low level atomic memory primitives provided directly by CPU instructions but without any ordering guarantees. Channels and mutexes guarantee the strict order of accesses to values being shared by go routines, and since these semantics are what we expect, it is often the better choice to use mutexes and channels. However, if you're just trying to ensure that a single operation happens correctly in isolation (such as tracking statistics), or if you're building concurrency primitives from scratch for advanced algorithms, then using atomics makes sense.

And here's why it makes sense:

```
BenchmarkCounterInc/Atomic-10         	170998743	         6.881 ns/op	1162.54 MB/s	       0 B/op	       0 allocs/op
BenchmarkCounterInc/Mutex-10          	65349984	        18.50 ns/op	 432.34 MB/s	       0 B/op	       0 allocs/op
BenchmarkCounterLoad/Atomic-10        	1000000000	         0.5131 ns/op	15590.98 MB/s	       0 B/op	       0 allocs/op
BenchmarkCounterLoad/Mutex-10         	87413383	        13.72 ns/op	 583.05 MB/s	       0 B/op	       0 allocs/op
```

On my Macbook Pro, using atomics to keep track of a counter is 3x faster for writes and and 26x faster for reads.

## Sources

- [Atomic Package Documentation](https://pkg.go.dev/sync/atomic)
- [StackOverflow: Is there a difference in Go between a counter using atomic operations and one using a mutex?](https://stackoverflow.com/questions/47445344/is-there-a-difference-in-go-between-a-counter-using-atomic-operations-and-one-us)

## Complete Code

The complete code and benchmark results on [gist](https://gist.github.com/bbengfort/44308aeab2d6def5899c7e34d189e945) can be found below:

{{< gist bbengfort 44308aeab2d6def5899c7e34d189e945 >}}