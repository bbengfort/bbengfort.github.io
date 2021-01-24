---
aliases:
- /snippets/2020/12/30/self-signed-ca.html
categories: snippets
date: '2020-12-30T15:51:06Z'
draft: false
showtoc: false
slug: self-signed-ca
title: Self Signed CA
---

I went on a brief adventure looking into creating a lightweight certificate authority (CA) in Go to issue certificates for mTLS connections between peers in a network. The CA was a simple command line program and the idea was that the certificate would initialize its own self-generated certs whose public key would be included in the code base of the peer-to-peer servers, then it could generate TLS x.509 key pairs signed by the CA. Of course you could do this with `openssl`, but I wanted to keep a self-coded Go version around for posterity.

Usage:

```
$ ca init -o "My P2P Network" -C "United States"
$ ca issue -o "Peer 1" -C "United States" -p "California"
$ ca issue -o "Peer 2" -C "France" -l "Paris"
```

The [gist](https://gist.github.com/bbengfort/465774ab2e8b45e372caf637aeed5776) is as follows:

{{< gist bbengfort 465774ab2e8b45e372caf637aeed5776 >}}

After usage there are a couple of key things that came up:

1. How do you generate serial numbers for the certificates?
2. Can you PEM encode the certificate along with the CA public key in a single CA file?
3. Can you PKCS12 encrypt the issued certificates for emailing?