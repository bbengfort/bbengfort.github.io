---
layout: post
title:  "Self Signed CA"
date:   2020-12-30 15:51:06 -0500
categories: snippets
---

I went on a brief adventure looking into creating a lightweight certificate authority (CA) in Go to issue certificates for mTLS connections between peers in a network. The CA was a simple command line program and the idea was that the certificate would initialize its own self-generated certs whose public key would be included in the code base of the peer-to-peer servers, then it could generate TLS x.509 key pairs signed by the CA. Of course you could do this with `openssl`, but I wanted to keep a self-coded Go version around for posterity.

Usage:

```
$ ca init -o "My P2P Network" -C "United States"
$ ca issue -o "Peer 1" -C "United States" -p "California"
$ ca issue -o "Peer 2" -C "France" -l "Paris"
```

<script src="https://gist.github.com/bbengfort/465774ab2e8b45e372caf637aeed5776.js"></script>

After usage there are a couple of key things that came up:

1. How do you generate serial numbers for the certificates?
2. Can you PEM encode the certificate along with the CA public key in a single CA file?
3. Can you PKCS12 encrypt the issued certificates for emailing?