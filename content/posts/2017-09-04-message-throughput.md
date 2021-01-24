---
categories: observations
date: "2017-09-04T17:20:06Z"
title: Messaging Throughput gRPC vs. ZMQ
---

Building distributed systems in Go requires an RPC or message framework of some sort. In the systems I build I prefer to pass messages serialized with [protocol buffers](https://developers.google.com/protocol-buffers/) therefore a natural choice for me is [grpc](https://grpc.io/). The grpc library uses HTTP2 as a transport layer and provides a code generator based on the protocol buffer syntax making it very simple to use.

For more detailed control, the [ZMQ](http://zeromq.org/) library is an excellent, low latency socket framework. ZMQ provides several communication patterns from basic REQ/REP (request/reply) to PUB/SUB (publish/subscribe). ZMQ is used at a lower level though, so more infrastructure per app needs to be built.

This leads to the obvious question: which RPC framework is faster? Here are the results:

![Echo Server Throughput]({{site.base_url }}/assets/images/2017-09-08-echo-throughput.png)

These results show the message throughput of three echo servers that respond to a simple message with a response including a sequence number. Each server is running on its own EC2 micro instance with 1GB of memory and 1 vCPU. Each client is running on on an EC2 nano instance with 0.5GB of memory and 1 vCPU and are constantly sending messages at the server. The throughput is the number of messages per second the server can handle.

The servers are as follows:

1. [rep](https://github.com/bbengfort/rtreq/blob/master/server_sync.go): a server that implements a REQ/REP socket and simple handler.
2. [router](https://github.com/bbengfort/rtreq/blob/master/server_async.go): a server that implements a REQ/ROUTER socket along with a DEALER/REP socket for 16 workers, connected via a proxy.
3. [grpc](https://github.com/bbengfort/echo/blob/master/server.go): implements a gRPC service.

The runner and results can be found [here](https://github.com/bbengfort/go-rpc-throughput).

## Discussion

All the figures exhibit a standard shape for throughput - namely as more clients are added the throughput increases, but begins to tail off toward an asymptote. The asymptote represents the maximum number of messages a server can respond to without message latency. Generally speaking if a server can handle multiple clients at once, the throughput is higher.   

The ZMQ REQ/ROUTER/PROXY/DEALER/REP server with 16 workers outperforms the gRPC server (it has a higher overall throughput). I hypothesize that this is because ZMQ does not have the overhead of HTTP and is in fact lighter weight code than gRPC since none of it is generated. It's unclear if adding more workers would improve the throughput of the ZMQ router server.

The performance of the REQ/REP server is a mystery. It's doing _way_ better than the other two. This socket has very little overhead, so for fewer clients it should be performing better. However, this socket also blocks on a per-client basis. Both grpc and router are asynchronous and can handle multiple clients at a time suggesting that they should be much faster.
