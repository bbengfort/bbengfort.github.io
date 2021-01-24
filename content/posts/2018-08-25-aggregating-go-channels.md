---
categories: snippets
date: "2018-08-25T08:28:59Z"
title: Aggregating Reads from a Go Channel
---

Here's the scenario: we have a buffered channel that's being read by a single Go routine and is written to by multiple go routines. For simplicity, we'll say that the channel accepts events and that the other routines generate events of specific types, `A`, `B`, and `C`. If there are more of one type of event generator (or some producers are faster than others) we may end up in the situation where there are a series of the same events on the buffered channel. What we would like to do is read _all_ of the same type of event that is on the buffered channel at once, handling them all simultaneously; e.g. aggregating the read of our events.

![Event Stream](/images/2018-08-25-event_channel.png)

An initial solution is composed of two loops; the first loop has a select that performs a blocking read of either the `msgs` or a `done` channel to determine when to exit the go routine. If a `msg` is received a second loop labeled grouper is initiated with a non blocking read of the `msgs` channel. The loop keeps track of a `current` and `next` value. If `next` and `current` are the same, it continues reading off the channel, until they are different or there is nothing to read at which point it handles both `next` and `current`.

```go
func consumeAggregate(msgs <-chan string, done <-chan bool) {
    var current, next string
    var count int

    for {
        // Outer select does a blocking read on both channels
        select {
        case current = <-msgs:
            // count our current event
            ecount = 1
        grouper:
            // continue reading events off the msgs channel
            for {
                select {
                case next = <-msgs:
                    if next != current {
                    // exit grouper loop and handle next and current
                    break grouper
                } else {
                    // keep track of the number of similar events
                    count++
                }
                default:
                    // nothing is on the channel, break grouper and
                    // only handle current by setting next to empty
                    next = ""
                    break grouper
                }
            }
        case <-done:
            // done consuming exit go routine
            return
        }

        // This section happens after select is complete
        // handle the current messages with the aggregate count
        handle(current, count)

        // handle next if one exists
        if next != "" {
            handle(next, 1)
        }
    }
}
```

This solution does have one obvious problem; the `next` value is not aggregated with similar values that happen after. E.g. in the event stream `aaaabbb`, the calls to `handle` will be `(a, 4)`, `(b, 1)`, `(b, 2)`. The good news though is that testing with the race and deadlock detector show that this method is correct. Possible improvements for a future post include:

- Aggregate the next value
- Read `val, ok` from the channel to detect if it's closed to exit
- convert the outer loop to a `range` to complete when the channel is closed

Here is the [Aggregating Channel Gist](https://gist.github.com/bbengfort/9b152a12a0291c5b5d403cbe6c8202ad) that contains the complete code and tests.
