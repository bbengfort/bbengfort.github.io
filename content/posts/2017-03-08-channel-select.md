---
aliases:
- /snippets/2017/03/08/channel-select.html
categories: snippets
date: '2017-03-08T10:52:39Z'
draft: false
showtoc: false
slug: channel-select
title: Using Select in Go
---

Ask a Go programmer what makes Go special and they will immediately say &ldquo;concurrency is baked into the language&rdquo;. Go's concurrency model is one of communication (as opposed to locks) and so concurrency primitives are implemented using _channels_. In order to synchronize across multiple channels, go provides the `select` statement.

A common pattern for me has become to use a `select` to manage broadcasted work (either in a publisher/subscriber model or a fanout model) by initializing go routines and passing them _directional channels_ for synchronization and communication. In the example below, I create a buffered channel for output (so that the workers don't block waiting for the receiver to collect data), a channel for errors (first error kills the program) and a timer to update the state of my process on a routine basis. The `select` waits for the first channel to receive a message and then continues processing. By keeping the `select` in a `for` loop, I can continually read of the channels until I'm done.

The pattern code is below:

{{< gist bbengfort 70c60a0c5fe89e0b6203e2d81e5a9aa2 >}}

The `worker` function does not return anything (since it's a go routine) but instead takes as input an id, and two directional channels &mdash; meaning that the go routines can only send on the channel and not receive. The first channel is the output channel and the second is for errors. The worker pretends to work with a random sleep then just reports back that it has been awakened.

The main function creates the output and error channels as well as a ticker, which has a timer channel on it. We then launch the go routines (keeping track of how many are running, similar to a `WaitGroup`). The `for` loop is basically `while True` &mdash; it loops until break or return. The `select` waits until a value comes in on one of the channels, at which point it handles that case and exits from that block (at which point we check if we should break, and if not we continue to block until we receive data on the channel). Even for long running processes, the ticker will cause the loop to iterate once per second, allowing us to manage our state or update the user. If an error occurs on any of the workers we kill the entire process rather than risk anything else.
