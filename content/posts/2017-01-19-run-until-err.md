---
categories: snippets
date: "2017-01-19T11:00:40Z"
title: Run Until Error with Go Channels
---

Writing systems means the heavy use of go routines to support concurrent operations. My current architecture employs several go routines to run a server for a simple web interface as well as command line app, file system servers, replica servers, consensus coordination, etc. Using multiple go routines (threads) instead of processes allows for easier development and shared resources, such as a database that can support transactions. However, management of all these threads can be tricky.

My current plan is to initialize thread-safe resources in a main thread, then pass those resources to the various go routines that need to do their `ListenAndServe` work. The main thread then listens on an error channel in case anything bad goes down that requires termination of the entire service. The first error that comes in will shut everything down, otherwise if no errors come in, then the main thread is just sitting there listening and managing everything overall.

As a reminder how to do this, here is a simple example:

{{< gist bbengfort 2b3f03e1b3c5a2efe05179158dd4d5d3 >}}

Basically the main function acts as the main thread here, initializing the error channel, then running 10 bomb threads who create random delays. Whichever bomb goes off first sends the error on the channel and the entire process quits. Simple!
