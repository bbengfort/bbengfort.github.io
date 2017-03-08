---
layout: post
title:  "Using Select in Go"
date:   2017-03-08 10:52:39 -0500
categories: snippets
---

Ask a Go programmer what makes Go special and they will immediately say &ldquo;concurrency is baked into the language&rdquo;. Go's concurrency model is one of communication (as opposed to locks) and so concurrency primitives are implemented using _channels_. In order to synchronize across multiple channels, go provides the `select` statement.

A common pattern for me has become to use a `select` to manage broadcasted work (either in a publisher/subscriber model or a fanout model) by initializing go routines and passing them _directional channels_ for synchronization and communication. In the example below, I create a buffered channel for output (so that the workers don't block waiting for the receiver to collect data), a channel for errors (first error kills the program) and a timer to update the state of my process on a routine basis. The `select` waits for the first channel to receive a message and then continues processing. By keeping the `select` in a `for` loop, I can continually read of the channels until I'm done.

The pattern code is below:

TODO: Change to a Gist snippet.

```go
package main

import (
	"fmt"
	"log"
	"math/rand"
	"time"
)

// Selects a random number of milliseconds to sleep then sends a message on
// the wake up channel back to the initiator.
func worker(idx int, wakeup chan<- string, echan chan<- error) {
	delay := time.Duration(rand.Int63n(int64(8000))) * time.Millisecond
	time.Sleep(delay)

	msg := fmt.Sprintf("worker %d slept for %s", idx, delay)
	wakeup <- msg
}

func main() {

	// Create communication channels
	ticker := time.NewTicker(time.Second * 1)
	wakeup := make(chan string, 10)
	echan := make(chan error)
	workers := 10

	// Launch 10 go routines
	for i := 0; i < workers; i++ {
		go worker(i+1, wakeup, echan)
	}

	var s string
	var e error
	var t time.Time

	for {
		// Select on timer, output, and error channels
		select {
		case t = <-ticker.C:
            // Routine state update
			fmt.Printf("tick at %s\n", t)
		case s = <-wakeup:
            // Handle output from a worker
			fmt.Printf("%s\n", s)
			workers--
		case e = <-echan:
            // If an error is received terminate
			log.Fatal(e)
		}

        // If there are no more workers, break
		if workers == 0 {
			break
		}
	}

}
```

The `worker` function does not return anything (since it's a go routine) but instead takes as input an id, and two directional channels &mdash; meaning that the go routines can only send on the channel and not receive. The first channel is the output channel and the second is for errors. The worker pretends to work with a random sleep then just reports back that it has been awakened.

The main function creates the output and error channels as well as a ticker, which has a timer channel on it. We then launch the go routines (keeping track of how many are running, similar to a `WaitGroup`). The `for` loop is basically `while True` &mdash; it loops until break or return. The `select` waits until a value comes in on one of the channels, at which point it handles that case and exits from that block (at which point we check if we should break, and if not we continue to block until we receive data on the channel). Even for long running processes, the ticker will cause the loop to iterate once per second, allowing us to manage our state or update the user. If an error occurs on any of the workers we kill the entire process rather than risk anything else. 
