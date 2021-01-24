---
categories: snippets
date: "2017-03-21T16:27:39Z"
title: Sanely gRPC Dial a Remote
---

In my systems I need to handle failure; so unlike in a typical client-server relationship, I'm prepared for the remote I'm dialing to not be available. Unfortunately when you do this with [gRPC-Go](https://godoc.org/google.golang.org/grpc) there are a couple of annoyances you have to address. They are (in order of solutions):

1. Verbose connection logging
2. Background and back-off for reconnection attempts
3. Errors are not returned on demand.
4. There is no ability to keep track of statistics

So first the logging. When you dial an unavailable remote as follows:

```go
conn, err := grpc.Dial(addr, grpc.WithInsecure())
if err != nil {
    return err
}

client := pb.NewServiceClient(conn)
resp = client.RPC()
```

You will get a lot of log messages in the form of:

```
2017/03/20 16:36:16 grpc: addrConn.resetTransport failed to create client transport: connection error: desc = "transport: dial tcp 192.168.1.1:port: getsockopt: connection refused"; Reconnecting to {addr:port <nil>}
2017/03/20 16:36:16 grpc: addrConn.resetTransport failed to create client 2017/03/20 16:36:16 grpc: addrConn.resetTransport failed to create client transport: connection error: desc = "transport: dial tcp 192.168.1.1:port: getsockopt: connection refused"; Reconnecting to {addr:port <nil>}
2017/03/20 16:36:16 grpc: addrConn.resetTransport failed to create client
...
```

And by a lot, I mean ... a lot; they will continue to spew for a while (probably at least 30 seconds). So to tackle that issue, we'll turn off the logging by creating a noop (nop, no-op) logger that doesn't do anything, and set it as the logger for `grpclog`. First the logger:

<script src="https://gist.github.com/bbengfort/b9345330339dee7fc04d6153b1a2eb91.js"></script>

As you can see, this logger meets the interface for a `SetLogger()` function, and we can set the grpc logger in our library's init as follows:

```go
func init() {
	// Set the random seed to something different each time.
	rand.Seed(time.Now().Unix())

	// Stop the grpc verbose logging
	grpclog.SetLogger(noplog)
}
```


Ok, onto the next two problems that are both solved with context. First, the call to `grpc.Dial()` happens in the background by default. This can cause panics due to nil dereference errors if you're not careful. Block until connected as follows:

```go
conn, err := grpc.Dial(addr, grpc.WithInsecure(), grpc.WithBlock())
```

Now it's up to you to handle concurrency with the connections. Of course blocking doesn't make a whole lot of sense until you limit it. And in fact, no `err` will be returned from the function unless you cause it to error with a timeout.  

```go
conn, err := grpc.Dial(
        addr, grpc.WithInsecure(), grpc.WithBlock(),
        grpc.WithTimeout(1 * time.Second)
)
```

Note that the `WithTimeout` option does not do anything if `WithBlock` is not used as well.

Coming Soon: using `WithStatsHandler()` to address the fourth issue.

And there is my basic start to managing the `grpc.Dial` function for scenarios when the remote may not be reachable. I'm sure there will be a lot more on this later.
