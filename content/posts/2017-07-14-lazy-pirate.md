---
categories: snippets
date: "2017-07-14T10:24:15Z"
title: Lazy Pirate Client
---

In the [last post]({% post_url 2017-07-13-zmq-basic %}) I discussed a simple REQ/REP pattern for ZMQ. However, by itself [REQ/REP is pretty fragile](http://dbeck.github.io/5-lessons-learnt-from-choosing-zeromq-and-protobuf/). First, every REQ requires a REP and a server can only handle one request at a time. Moreover, if the server fails in the middle of a reply, then everything is hung. We need more reliable REQ/REP, which is actually the subject of [an entire chapter](http://zguide.zeromq.org/page:all#toc86) in the ZMQ book.

For my purposes, I want to ensure that repliers (servers) can fail without taking out the client. The server can simply `sock.Send(zmq.DONTWAIT)` to deal with clients that dropout before the communication is complete. Server failure is a bit more difficult to deal with, however. Client side reliability is based on timeouts and retries, dealing with failed messages. ZMQ calls this the [Lazy Pirate Pattern](http://zguide.zeromq.org/page:all#Client-Side-Reliability-Lazy-Pirate-Pattern).

This is a pretty big chunk of code, but it creates a `Client` object that wraps a socket and performs lazy pirate sends. The primary code is in the `Reset()` and `Send()` methods. The `Reset()` method sets the linger to zero in order to close the connection immediately without errors; it then closes the connection and reconnects thereby resetting the state to be able to send messages again. This is "brute force but effective and reliable".

The `Send()` method fires off a message then uses a `zmq.Poller` with a timeout to keep checking if a message has been received in that time limit. If it was successful, then great! Otherwise we decrement our retries and try again. If we're out of retries there is nothing to do but return an error. The code is here:

{{< gist bbengfort 7fa15777320cfb27599567a5585f3ba8 >}}

This code is fairly lengthy, but as it turns out, most of the content for both clients and servers on either side of REQ/REP have similar wrapper code for context, socket, and connection/bind wrapping. So far it's been very reliable in my code to allow servers to drop out and fail without blocking clients or other nodes in the network.
