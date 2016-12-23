---
layout: post
title:  "Benchmarking Readline Iterators"
date:   2016-12-23 10:18:01 -0500
categories: programmer
---

I'm starting to get serious about programming in Go, trying to move from an intermediate level to an advanced/expert level as I start to build larger systems. Right now I'm working on a problem that involves on demand iteration, and I don't want to pass around entire arrays and instead be a bit more frugal about my memory usage. Yesterday, I discussed using [channels to yield iterators from functions]({% post_url 2016-12-22-yielding-functions-for-iteration-golang %}) and was a big fan of the API, but had some questions about memory usage. So today I created a package, [iterfile](https://github.com/bbengfort/iterfile) to benchmark and profile various iteration constructs in Go.

Based on Ewan Cheslack-Postava's [Iterators in Go](https://ewencp.org/blog/golang-iterators/) post, I created iteration functions for line-by-line reading of a file (`Readlines`), including the channel method, a method using callbacks, and a stateful iterator method that uses a struct to keep track of iteration (for funsies, I also added a Python implementation). Without further ado, here are the results:

![Memory Profiling of Readlines Iteration for a 3.9G Text File]({{site.base_url }}/assets/images/2016-12-23-memory-profile-readlines.png)

I used an external process to sample the memory of the readlines process every 0.01 seconds, using [mprof](https://pypi.python.org/pypi/memory_profiler) by Fabian Pedregosa and Philippe Gervais. The four readlines implementations opened a large text file (3.9GB) with 900,002 lines of text containing random lengths of "fizz buzz foo bar baz" words, counting the total number of characters by summing the length of each line.

The python process took by far the longest and most memory as expected. The channel iterator implementation took almost as long as Python, but surprisingly used the least amount of memory. The callback and iterator implementations were the quickest, each using similar amounts of memory. Go benchmarks (`go test -bench=.`) for each function (except Python) are as follows:

```
BenchmarkChanReadlinesSmall-8              20000         74958 ns/op
BenchmarkChallbackReadlinesSmall-8         50000         28836 ns/op
BenchmarkIteratorReadlinesSmall-8          50000         29006 ns/op

BenchmarkChanReadlinesMedium-8              2000        621716 ns/op
BenchmarkChallbackReadlinesMedium-8        10000        216734 ns/op
BenchmarkIteratorReadlinesMedium-8         10000        219842 ns/op

BenchmarkChanReadlinesLarge-8                200       6250004 ns/op
BenchmarkChallbackReadlinesLarge-8          1000       2198904 ns/op
BenchmarkIteratorReadlinesLarge-8           1000       2229104 ns/op
```

As a result I'll probably be using the stateful iterator approach more often in my code, reserving the channel method only when performance is not required, but a clear API is. Stay tuned for a post on writing stateful iterators. 
