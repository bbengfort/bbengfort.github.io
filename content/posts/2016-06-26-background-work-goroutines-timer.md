---
aliases:
- /snippets/2016/06/26/background-work-goroutines-timer.html
categories: snippets
date: '2016-06-26T06:52:38Z'
draft: false
showtoc: false
slug: background-work-goroutines-timer
title: Background Work with Goroutines on a Timer
---

As I'm moving deeper into my PhD, I'm getting into more Go programming for the systems that I'm building. One thing that I'm constantly doing is trying to create a background process that runs forever, and does some work at an interval. Concurrency in Go is native and therefore the use of threads and parallel processing is very simple, syntax-wise. However I am still solving problems that I wanted to make sure I recorded here.

Today's problem involves getting a go routine to execute a function on an interval, say every 5 seconds or something like that. The foreground process will presumably be working until finished, and we want to make sure it can gracefully shutdown the background process without a delay. In order to communicate between threads in Go, you have to use a channel. I've put together the work from [Timer Routines And Graceful Shutdowns In Go](https://www.goinggo.net/2013/09/timer-routines-and-graceful-shutdowns.html) into a single snippet to remind myself how to do this:

{{< gist bbengfort 277b8647a626684fa993cde6f0add81c >}}

The end result is a program that looks like this:

```bash
$ go run main.go
2016/06/25 21:27:51 Main started
2016/06/25 21:27:51 Worker Started
2016/06/25 21:27:58 Action complete!
2016/06/25 21:28:03 Action complete!
2016/06/25 21:28:11 Main out!
```

As you can see it's seven seconds between "Worker Started" and the first "Action Complete!" (5 second delay plus 2 seconds work). The second "Action Complete!" is 5 seconds later however because the worker only waits 3 seconds to make up for the work time from the previous interval. Shutdown is called, and the program gracefully shuts down with no more actions.
