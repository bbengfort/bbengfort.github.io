---
layout: post
title:  "Yielding Functions for Iteration in Go"
date:   2016-12-22 06:54:26 -0500
categories: snippets
---

It is very common for me to design code that expects functions to return an iterable context, particularly because I have been developing in Python with the `yield` statement. The `yield` statement allows functions to &ldquo;return&rdquo; the execution context to the caller while still maintaining state such that the caller can return state to the function and continue to iterate. It does this by actually returning a `generator`, iterable object constructed from the local state of the closure.

Now that I'm programming in Go, I often want to apply the same pattern, but iteration in Go is very different and is conducted at a slightly lower level. Go does have an iteration construct, `range`, that allows easy iteration over collection data structures, similar to a for each in construct. The good news is that `range` also works to collect elements from a `channel`, which means that an opportunity presents itself to create Go functions that yield by combining goroutines and channels.

Consider the following example that implements similar (but simple) functionality as Python's `xrange` iterator, allowing us to loop over the numbers from zero to the limit stepping by 1:

<script src="https://gist.github.com/bbengfort/26667087df733029b51b088acf397633.js"></script>

The function returns a channel of integers, to which `range` can be applied. We give up the execution context of our inner loop by running the loop in a goroutine, which sends its results to the caller using the channel as a synchronization mechanism. So long as _we ensure to close the channel after iteration_ - this function works as expected:

```go
for i := range XRange(10) {
    fmt.Println(i)
}
```

This pattern speaks to me, it is exactly how I think about constructing iterable functions. As a result, I have a bit less cognitive load than if I had to design stateful iterators and manage calls to `Next()` and `HasNext()` or something like that. This simple programming construct (which is Go idiomatic) does come at some performance cost -- Go now has to manage the thread and the communication of the channel. Potentially a solution is to use [buffered channels](http://openmymind.net/Introduction-To-Go-Buffered-Channels/), which will allow the iteration to store more information on the channel as the iterator is slow to collect it.

I do have some questions about this though, that I hope to answer in the future. Consider the following function for reading a file line by line:

<script src="https://gist.github.com/bbengfort/4d51fc91876adde38502b7189df05d20.js"></script>

This is very common utility code for me, pass in a path, open the file, and read the file one line at a time, buffering in memory only the line of text. Particularly for reading large files, we need to ensure that we minimize the amount of memory we use. The way that I use this function is as follows:

```go
reader, err := Readlines("myfile.txt")
if err != nil {
    log.Fatal(err)
}

for line := reader {
    fmt.Println(line)
}
```

But it does leave me with a few questions:

1. What is the memory usage of the goroutine vs. the caller particularly for large files?
2. Is it possible for the goroutine to get ahead of the caller and load huge chunks of data into memory before it can be collected?
3. Speaking of collection, how exactly do lines in the file get cleaned up?

I think I'd like to do some benchmarking tests with several files and large files using closures for iteration, channels as in this post, and more standard stateful iterator objects; comparing the use of memory and speed of reads. But I'll save that for a later post!
