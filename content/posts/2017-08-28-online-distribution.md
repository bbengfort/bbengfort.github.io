---
categories: snippets
date: "2017-08-28T12:49:46Z"
title: Online Distribution
---

This post started out as a discussion of a `struct` in Go that could keep track of online statistics without keeping an array of values. It ended up being a lesson on over-engineering for concurrency.

The spec of the routine was to build a data structure that could keep track of internal statistics of values over time in a space-saving fashion. The primary interface was a method, `Update(sample float64)`, so that a new sample could be passed to the structure, updating internal parameters. At conclusion, the structure should be able to describe the mean, variance, and range of all values passed to the update method. I created two versions:

1. A thread-safe version using mutexes, but blocking on `Update()`
2. A thread-safe version using a channel and a go routine so that `Update()` was non-blocking.

I ran some benchmarking, and discovered that the blocking implementation of `Update` was actually far faster than the non-blocking version. Here are the numbers:

```
BenchmarkBlocking-8      	20000000            81.1 ns/op
BenchmarkNonBlocking-8   	10000000	       140 ns/op
```

Apparently, putting a float on a channel, even a buffered channel, incurs some overhead that is more expensive than simply incrementing and summing a few integers and floats. I will present both methods here, but note that the _first_ method (blocking update) should be implemented in production.

> You can find this code at [github.com/bbengfort/x/stats](https://godoc.org/github.com/bbengfort/x/stats) if you would like to use it in your work.

## Online Descriptive Statistics (Blocking)

To track statistics in an online fashion, you need to keep track of the various aggregates that are used to compute the final descriptives statistics of the distribution. For simple statistics such as the minimum, maximum, standard deviation, and mean you need to track the number of samples, the sum of samples, and the sum of the squares of all samples (along with the minimum and maximum value seen). Here is how you do that:

{{< gist bbengfort d730797778d26259b2a0ad3e72ca52c9 >}}

I use this data structure as a lightweight mechanism to keep track of online statistics for experimental results or latency. It gives a good overall view of incoming values at very little expense.

## Non-blocking Update

In an attempt to improve the performance of this method, I envisioned a mechanism where I could simply dump values into a [buffered channel](https://tour.golang.org/concurrency/3) then run an `updater` go routine to collect values and perform the online computation. The updater function can simply `range` over the channel, and the channel can be closed to stop the goroutine and finalize anything still on the channel. This is written as follows:

{{< gist bbengfort 3059589e61639b9ca4932fd8dff01bfd >}}

The lesson was that this is actually less performant, no matter how large the buffer is. I increased the buffer size to 10000001 to ensure that the sender could not block, but I still received 116 ns/op benchmarks. Generally, this style is what I use when the function being implemented is actually pretty heavy (e.g. writes to disk). In this case, the function was too lightweight to matter!
