---
layout: post
title:  "Synchronization in Write Throughput"
date:   2018-02-13 07:10:06 -0500
categories: observations
---

This post details as yet unexplained observations about synchronization to a single writer in Go &mdash; namely as the number of threads increases the throughput of writes decreases. There seems to be some lock contention issues, or potentially I'm simply computing throughput incorrectly. As I'm investigating, I've put up a simple library called [syncwrite](https://github.com/bbengfort/syncwrite) to benchmark this code.

Here is the use case: consider a system that has multiple goroutines, each of which want to append to a log file on disk. The append-only log determines the sequence or ordering of events in the system, so appends must be atomic and reads to an index in the log, idempotent. The interface of the Log is as follows:

```go
type Log interface {
	Open(path string) error
	Append(value []byte) error
	Get(index int) (*Entry, error)
	Close() error
}
```

The log embeds `sync.RWMutex` to ensure no race conditions occur and that our read/write invariants are met. The `Open`, `Append`, and `Close` methods are all protected by a write lock, and the `Get` method is protected with a read lock. The structs that implement `Log` all deal with the disk and in-memory storage in different ways:

- `InMemoryLog`: appends to an in-memory slice and does not write to disk.
- `FileLog`: on open, reads entries from file into in-memory slice and reads from it, writes append to both the slice and the file.
- `LevelDBLog`: both writes and reads go to a LevelDB database.

In the future (probably in the next post), I will also implement an `AsyncLog` that wraps a Log and causes write operations to be asynchronous by storing them on a channel and allowing the goroutine to immediately return.

## Benchmarks

The benchmarks are associated with an _action_, which can be one or more operations to disk. In this benchmark we simply evaluate an action that calls the `Write` method of a log with `"foo"` as the value. Per-action benchmarks are computed using `go-bench`, which computes the average time it takes to run the action once:

```
BenchmarkInMemoryLog-8   	10000000	       201 ns/op
BenchmarkFileLog-8       	  200000	      7253 ns/op
BenchmarkLevelDBLog-8    	  100000	     12104 ns/op
```

Writing to the in-memory log is by far the fastest, while writing to the LevelDB log is by far the slowest operation. We expect _throughput_, that is the number of operations per second, to be equivalent with these per-action benchmarks in a single thread. The question is how throughput changes with more threads.

Throughput benchmarks are conducted by running `t` threads, each of which run `n` actions and returns the amount of time it takes to run all `n` actions. The total number of operations performed is `n*t` and this is divided by the total number of seconds across all go routines to get the number of operations per second. We observed the following decreasing throughput as the number of threads increased:

![Sync Write Throughput with Increasing # of Threads]({{site.base_url }}/assets/images/2018-02-13-sync-write-throughput.png)

Note that the y-axis is on a logarithm scale, so the seemingly linear decrease in the chart actually exposes an exponential decrease. The raw numbers are as follows:

|           |     1 Threads |     2 Threads |     4 Threads |   8 Threads |
|-----------|--------------:|--------------:|--------------:|------------:|
| In-Memory | 7,183,448.018 | 3,779,715.176 | 1,204,300.998 | 583,877.489 |
| File      |   154,304.171 |    41,878.633 |    21,346.001 |  16,061.860 |
| LevelDB   |    87,358.272 |    31,241.465 |    16,052.638 |   9,298.797 |

## Observations

As the number of threads increases there seems to be increased contention for the locks on the Log, but I'm unsure why this is causing a massive slowdown. Potentially there is a scheduling issue with the processor, such that the threads and the main process that is locking are contending for system resources. Another consideration is that perhaps the garbage collector is getting overwhelmed by so many threads generating data. Finally, it could simply be that my throughput computation is incorrect.

While I would expect that the throughput decreases as the number of threads increases, I wouldn't expect it to decrease quite so much. Because this type of data structure is routinely part of the applications I create (e.g. a server process that respond to multiple clients in different threads and writes to a central store in a safe manner), it is important to solve this issue. 
