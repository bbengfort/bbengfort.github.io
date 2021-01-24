---
aliases:
- /programmer/2017/03/03/secure-grpc.html
categories: programmer
date: '2017-03-03T09:41:39Z'
draft: false
showtoc: false
slug: secure-grpc
title: Secure gRPC with TLS/SSL
---

One of the primary requirements for the systems we build is something we call the &ldquo;minimum security requirement&rdquo;. Although our systems are not designed specifically for high security applications, they must use minimum standards of encryption and authentication. For example, it seems obvious to me that a web application that [stores passwords](https://docs.djangoproject.com/en/1.10/topics/auth/passwords/) or [credit card information](https://www.pcisecuritystandards.org/) would encrypt their data on disk on a per-record basis with a [salted hash](https://www.codeproject.com/Articles/704865/Salted-Password-Hashing-Doing-it-Right). In the same way, a distributed system must be able to handle [encrypted blobs](https://www.usenix.org/legacy/event/osdi04/tech/full_papers/li_j/li_j.pdf), [encrypt all inter-node communication](http://blog.cloudera.com/blog/2013/03/how-to-set-up-a-hadoop-cluster-with-network-encryption/), and [authenticate and sign all messages](https://alexbilbie.com/2012/11/hawk-a-new-http-authentication-scheme/). This adds some overhead to the system but the cost of overhead is far smaller than the cost of a breach, and if minimum security is the baseline then the overhead is just an accepted part of doing business.

For inter-replica communication we are currently using [gRPC](http://www.grpc.io/), an multi-platform RPC framework that uses [protocol buffers](https://developers.google.com/protocol-buffers/) for message serialization (we have also used [zeromq](http://zeromq.org/) in the past). The nice part about gRPC is that it has [authentication baked-in](http://www.grpc.io/docs/guides/auth.html) and promotes the use of SSL/TLS to authenticate and encrypt exchanges. The not so nice part is that while the gRPC tutorial has examples in [Ruby](http://www.grpc.io/docs/guides/auth.html#ruby), [C++](http://www.grpc.io/docs/guides/auth.html#c), [C#](http://www.grpc.io/docs/guides/auth.html#c-1), [Python](http://www.grpc.io/docs/guides/auth.html#python), [Java](http://www.grpc.io/docs/guides/auth.html#java), [Node.js](http://www.grpc.io/docs/guides/auth.html#nodejs), and [PHP](http://www.grpc.io/docs/guides/auth.html#php) there is no guide for Go (at the time of this post). This post is my attempt to figure it out.

From the [documentation](http://www.grpc.io/docs/guides/auth.html):

> gRPC has SSL/TLS integration and promotes the use of SSL/TLS to authenticate the server, and encrypt all the data exchanged between the client and the server. Optional mechanisms are available for clients to provide certificates for mutual authentication.

I'm primarily interested in the first part &mdash; authenticate the server and encrypt the data exchanged. However, the idea of [mutual TLS](https://en.wikipedia.org/wiki/Mutual_authentication) is something I hadn't considered before this investigation. My original plan was to use [Hawk](https://github.com/hueniverse/hawk) client authentication and message signatures. But potentially that's not something I have to do. So this post has two phases:

1. Encrypted communication using TLS/SSL from the server
2. Authenticated, mutual TLS using a certificate authority

Since all replicas in my system are both servers and clients, I think that it wouldn't make much sense not to do mutual TLS. After all, we're already creating certificates and exchanging keys and whatnot.

## Creating SSL/TLS Certificates

It seems like step one is to generate certificates and key files for encrypting communication. I thought this would be fairly straightforward using `openssl` from the command line, and it is (kind of) though there are a lot of things to consider. First, the files we need to generate:

- `server.key`: a private RSA key to sign and authenticate the public key  
- `server.pem`/`server.crt`: self-signed [X.509](https://en.wikipedia.org/wiki/X.509) public keys for distribution
- `rootca.crt`: a certificate authority public key for signing .csr files
- `host.csr`: a certificate signing request to access the CA

So there are a lot of files and a lot of extensions, many of which are duplicates or synonyms (or simply different encodings). I think that's primarily what's made this process so difficult. So to generate some simple .key/.crt pairs using `openssl`:

```
$ openssl genrsa -out server.key 2048
$ openssl req -new -x509 -sha256 -key server.key \
              -out server.crt -days 3650
```

The first command will generate a 2048 bit RSA key (stronger keys are available as well). The second command will generate the certificate, and will also prompt you for some questions about the location, organization, and contact of the certificate holder. These fields are pretty straight forward, but probably the most important field is the "Common Name" which is typically composed of the host, domain, or  IP address related to the certificate. The name is then used during verification and if the host doesn't match the common name a warning is raised.

Finally, to generate a certificate signing request (.csr) using `openssl`:

```
$ openssl req -new -sha256 -key server.key -out server.csr
$ openssl x509 -req -sha256 -in server.csr -signkey server.key \
               -out server.crt -days 3650
```

So this is pretty straightforward on the command line. However, it may be simpler to use [certstrap](https://github.com/square/certstrap), a simple certificate manager written in Go by the folks at [Square](http://square.github.io/). The app avoids dealing with openssl (and therefore raises questions about security in implementation), but has a very simple workflow: create a certificate authority, sign certificates with it.

To create a new certificate authority:

```
$ certstrap init --common-name "umd.fluidfs.com"
Created out/umd.fluidfs.com.key
Created out/umd.fluidfs.com.crt
Created out/umd.fluidfs.com.crl
```

To request a certificate for a specific host:

```
$ certstrap request-cert -ip 192.168.1.18
Created out/192.168.1.18.key
Created out/192.168.1.18.csr
```

And finally to generate the certificate for the host:

```
$ certstrap sign 192.168.1.18 --CA umd.fluidfs.com
Created out/192.168.1.18.crt from out/192.168.1.18.csr signed by
out/umd.fluidfs.com.key
```

Probably the most interesting opportunity for me is the ability to use `certstrap` programmatically to automatically generate keys. However, some review will have to be done into how safe it is.

## Encrypted Server

The simplest method to encrypt communication using gRPC is to use server-side TLS. This means that the server needs to be initialized with a public/private key pair and the client needs to have the server's public key in order to make the connection. I've created a small application called `sping` (secure ping) that basically does an echo request from a client to a server ([example repository](https://github.com/bbengfort/sping)). The server code is as follows:

```go

var (
    crt = "server.crt"
    key = "server.key"
)

func (s *PingServer) Serve(addr string) error {

    // Create the channel to listen on
    lis, err := net.Listen("tcp", addr)
    if err != nil {
        return fmt.Errorf("could not list on %s: %s", addr, err)
    }

    // Create the TLS credentials
    creds, err := credentials.NewServerTLSFromFile(crt, key)
    if err != nil {
        return fmt.Errorf("could not load TLS keys: %s", err)
    }

    // Create the gRPC server with the credentials
    srv := grpc.NewServer(grpc.Creds(creds))

    // Register the handler object
    pb.RegisterSecurePingServer(srv, s)

    // Serve and Listen
    if err := srv.Serve(lis); err != nil {
        return fmt.Errorf("grpc serve error: %s", err)
    }

    return nil
}
```

So the steps to the server are pretty straight forward. First, create a TCP connection on the desired address (e.g. pass in `":3264"` to listen on the external address on port 3264). Second, load the TLS credentials from their respective key files (both the private and the public keys), then initialize the grpc server with the credentials. Finally, register the handler for the service you implemented (here I'm using a method call on a struct that does implement the handler) and serve.

To get the client connected, you need to give it the `server.crt` (or `server.pem`) public key. In normal operation, this key can be fetched from a certificate authority, but since we're doing internal RPC, the public key must be shipped with the application.

```go
var cert = "server.crt"

func (c *PingClient) Ping(addr string, ping *pb.Ping) error {

    // Create the client TLS credentials
    creds, err := credentials.NewClientTLSFromFile(cert, "")
    if err != nil {
        return fmt.Errorf("could not load tls cert: %s", err)
    }

    // Create a connection with the TLS credentials
    conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(creds))
    if err != nil {
        return fmt.Errorf("could not dial %s: %s", addr, err)
    }

    // Initialize the client and make the request
    client := pb.NewSecurePingClient(conn)
    pong, err := client.Echo(context.Background(), ping)
    if err != nil {
        return fmt.Errof("could not ping %s: %s", addr, err)
    }

    // Log the ping
    log.Printf("%s\n", pong.String())
    return nil
}
```

Again, this is a fairly straight forward process that adds only three lines and modifies one from the original code. First load the server public key from a file into the credentials object, then pass the transport credentials into the grpc dialer. This will cause GRPC to initiate the TLS handshake every time it sends an echo RPC.

## Mutual TLS with Certificate Authority

The real problem with using the above method _and_ HAWK authentication is that every single replica will have to maintain both a server public key and a HAWK key for every other node in the system. That frankly sounds like a headache to me. Instead, we'll have every replica (client and server both) load their own public/private key pairs, then load the public keys of a CA (certificate authority) .crt file. Because all client public keys are signed by the CA key, the server and client can exchange and authenticate private keys during communication.

**CAVEAT**: when a client connects to a server, it must know the `ServerName` property to pass into the `tls.Config` object. This `ServerName` appears to have to be in agreement with the common name in the certificate.

The server code is now modified to create X.509 key pairs directly and to create a certificate pool based on the certificate authority public key.

```go
var (
    crt = "server.crt"
    key = "server.key"
    ca  = "ca.crt"
)

func (s *PingServer) Serve(addr string) error {

    // Load the certificates from disk
    certificate, err := tls.LoadX509KeyPair(crt, key)
    if err != nil {
        return fmt.Errorf("could not load server key pair: %s", err)
    }

    // Create a certificate pool from the certificate authority
    certPool := x509.NewCertPool()
    ca, err := ioutil.ReadFile(ca)
    if err != nil {
        return fmt.Errorf("could not read ca certificate: %s", err)
    }

    // Append the client certificates from the CA
    if ok := certPool.AppendCertsFromPEM(ca); !ok {
        return errors.New("failed to append client certs")
    }

    // Create the channel to listen on
    lis, err := net.Listen("tcp", addr)
    if err != nil {
        return fmt.Errorf("could not list on %s: %s", addr, err)
    }

    // Create the TLS credentials
    creds := credentials.NewTLS(&tls.Config{
    	ClientAuth:   tls.RequireAndVerifyClientCert,
    	Certificates: []tls.Certificate{certificate},
    	ClientCAs:    certPool,
    })

    // Create the gRPC server with the credentials
    srv := grpc.NewServer(grpc.Creds(creds))

    // Register the handler object
    pb.RegisterSecurePingServer(srv, s)

    // Serve and Listen
    if err := srv.Serve(lis); err != nil {
        return fmt.Errorf("grpc serve error: %s", err)
    }

    return nil
}
```

So quite a bit more work here than in the first version. First, we load the server key pair from disk into a `tls.Certificate` struct. Then we create a certificate pool, read the CA certificate from disk and append it to the pool. That done, we can create our TLS credentials. Importantly, our server will require client certificates for verification, and we specify the pool as our client certificate authority. Finally we pass our certificates into the configuration and create new TLS grpc server options, passing them into the `grpc.NewServer` function. The client code is very similar:

```go
var (
    crt = "client.crt"
    key = "client.key"
    ca  = "ca.crt"
)

func (c *PingClient) Ping(addr string, ping *pb.Ping) error {

    // Load the client certificates from disk
    certificate, err := tls.LoadX509KeyPair(crt, key)
    if err != nil {
        return fmt.Errorf("could not load client key pair: %s", err)
    }

    // Create a certificate pool from the certificate authority
    certPool := x509.NewCertPool()
    ca, err := ioutil.ReadFile(ca)
    if err != nil {
        return fmt.Errorf("could not read ca certificate: %s", err)
    }

    // Append the certificates from the CA
    if ok := certPool.AppendCertsFromPEM(ca); !ok {
        return errors.New("failed to append ca certs")
    }

    creds := credentials.NewTLS(&tls.Config{
        ServerName:   addr, // NOTE: this is required!
        Certificates: []tls.Certificate{certificate},
        RootCAs:      certPool,
    })

    // Create a connection with the TLS credentials
    conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(creds))
    if err != nil {
        return fmt.Errorf("could not dial %s: %s", addr, err)
    }

    // Initialize the client and make the request
    client := pb.NewSecurePingClient(conn)
    pong, err := client.Echo(context.Background(), ping)
    if err != nil {
        return fmt.Errof("could not ping %s: %s", addr, err)
    }

    // Log the ping
    log.Printf("%s\n", pong.String())
    return nil
}
```

The primary difference here being that we load _client certificates_ as opposed to the server certificate and that we specify `RootCAs` instead of `ClientCAs` in the TLS config. One final, important point, is that we also must specify the `ServerName`, whose value must match the common name on the certificate.

## Go Client

In this section, I will describe the method for a client connecting to a secure RPC in the same style as the [gRPC authentication examples](http://www.grpc.io/docs/guides/auth.html#examples). These examples use the [greeter quick start](http://www.grpc.io/docs/quickstart/go.html) code and perhaps they can be contributed back to the grpc.io documentation. Frankly, though, they're just a guess so hopefully the [PR](https://github.com/grpc/grpc.github.io/pull/469/commits/331b5fa12c8932f66ab96c26661b1a6f77768d1a) I submitted gets reviewed thoroughly.

### Base case - No encryption or authentication

```go
import (
    "google.golang.org/grpc"
    pb "google.golang.org/grpc/examples/helloworld/helloworld"
)

channel, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
client := pb.NewGreeterClient(channel)
```

### With server authentication SSL/TLS

```go
import "google.golang.org/grpc/credentials"

creds := credentials.NewClientTLSFromFile("roots.pem", "")
channel, _ := grpc.Dial(
    "localhost:443", grpc.WithTransportCredentials(creds)
)
client := pb.NewGreeterClient(channel)
```

### Authenticate with Google

```go
import "google.golang.org/grpc/credentials/oauth"

auth, _ := oauth.NewApplicationDefault(context.Background(), "")
channel, _ := grpc.Dial(
    "greeter.googleapis.com", grpc.WithPerRPCCredentials(auth)
)
client := pb.NewGreeterClient(channel)
```

## Conclusion

Always use SSL/TLS to encrypt communications and authenticate nodes. It is an open question about how to manage certificates in a larger system, but potentially an internal certificate authority resolves these problems. Getting secure communications up and running isn't necessarily the easiest part of distributed systems, but it is worth taking the time out to do it right. And finally, gRPC, please update your documentation.

Other Resources:

- [Secure Ping on GitHub](https://github.com/bbengfort/sping)
- [Using gRPC with Mutual TLS in Golang](http://krishicks.com/post/grpc-mutual-tls-golang/)
- [Simple GolangHTTPS/TLS Examples](https://gist.github.com/denji/12b3a568f092ab951456)
