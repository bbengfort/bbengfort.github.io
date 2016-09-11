---
layout: post
title:  "Parallel Enqueue and Workers"
date:   2016-09-07 14:29:51 -0400
categories: snippets
---

I was recently asked about the parallelization of both the enqueuing of tasks and their processing. This is a tricky subject because there are a lot of factors that come into play. For example do you have two parallel phases, e.g. a map and a reduce phase that need to be synchronized, or is there some sort of data parallelism that requires multiple tasks to be applied to the data (e.g. Storm-style topology). While there are a lot of tools for parallel processing in batch for large data sets, how do you take care of simple problems with large datasets (say hundreds of gigabytes) on a single machine with a quad core or hyperthreading multiprocessor?

For quick Python scripts, you have to use the `multiprocessing` module in order to get parallelism. Now adays, `multiprocessing` has a very nice interface with the `Pool` and `map_async` or `apply_async` functions. However, consider the following situation:

1. You have several CSV files that you want to process on a row-by-row basis.
2. For each row, you have to do an independent computation that is CPU bound.
3. You want to reduce the results of the per-row computations sequentially.

For example, consider the construction of a bloom filter from a list of multiple CSV files; you'll have to do parsing, hashing, filtering, aggregation, etc. on each row, then build the bloom filter from the bottom up. To do this, we'll use two parallel stages:

1. Multiple processes reading multiple CSV files, parsing each row and enqueuing it.
2. Multiple processes reading the queue of parsed rows and doing computation, then pushing the results to a done queue.

I've had to reuse a bit of code from a few places, and this is untested, but I think it demonstrates what is happening:

<script src="https://gist.github.com/bbengfort/09192d108a4998c1cbcb009861bd8e29.js"></script>


The `enqueue` function takes a path to a csv file as well as a synchronized queue (that uses locks to ensure only one process has access to the queue at a time). It reads each row from the CSV file, parses it, and puts it onto the queue. This type of work is similar to the `map` phase of MapReduce.

The `worker` function sits and watches an input queue, and attempts to get values of the queue with a timeout of 10 seconds. If the timeout expires or it sees the string `'STOP'` then it will break (exiting the forever watching loop) and return. Thus if a row gets added to the input queue within 10 seconds of the last time it fetched a row, the worker will continue working. It then does some computations (e.g. the function could save state and do a reduction, building a partial bloom filter, or other CPU/IO sensitive work). It then puts the results of its computation on the results queue.

The `parallelize` function is the primary process and coordinates both the enqueuing and the workers. It first sets up the two queues, the tasks (parsed rows) and results. It then creates a pool for the enqueue processes and uses `map_async` which will call the callback once all processes are complete. At that point, we simply put the `'STOP'` semaphore into the queue so that the workers know there are no more rows. We then create each worker, not using a pool, but just creating direct processes to watch the input queue and do other work. We then join on all these process to wait until they've terminated.

For simple tasks this workflow can get you a lot of raw performance for free, though if this is more routine type workflow, you may want to consider a language with concurrency built in -- like Go. 
