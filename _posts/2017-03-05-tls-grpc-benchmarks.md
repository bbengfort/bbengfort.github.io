---
layout: post
title:  "Benchmarking Secure gRPC"
date:   2017-03-05 17:26:24 -0500
categories: snippets
---

A natural question to ask after the previous post is &ldquo;how much overhead does security add?&rdquo; So I've benchmarked the three methods discussed; mutual TLS, server-side TLS, and no encryption. The results are below:

[![Secure gRPC Benchmarks]({{site.base_url }}/assets/images/2017-03-05-benchmark.png)]({{site.base_url }}/assets/images/2017-03-05-benchmark.png)

Here are the numeric results for one of the runs:

```
BenchmarkMutualTLS-8   	     200	   9331850 ns/op
BenchmarkServerTLS-8   	     300	   5004505 ns/op
BenchmarkInsecure-8    	    2000	   1179252 ns/op
PASS
ok  	github.com/bbengfort/sping	7.364s
```

Here is the code for the benchmarking for reference:

```go
var (
	server *PingServer
	client *PingClient
)

func BenchmarkMutualTLS(b *testing.B) {

	logmsgs = false
	server = NewServer()
	client = NewClient("tester", 100, 8)

	go server.ServeMutualTLS(50051)
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		_, err := client.PingMutualTLS("localhost:50051")
		if err != nil {
			fmt.Println(err)
			break
		}
	}

}
```

It's all pretty straight forward, the other two functions use `server.ServeTLS` and `server.ServeInsecure` for the server side and `client.PingTLS` and `client.PingInsecure` for the client. The only note is that because the server is running throughout the tests, each benchmark runs with a different port number. 
