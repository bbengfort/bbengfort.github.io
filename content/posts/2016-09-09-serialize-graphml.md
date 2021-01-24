---
categories: snippets
date: "2016-09-09T17:13:13Z"
title: Serializing GraphML
---

This is mostly a post of annoyance. I've been working with graphs in Python via NetworkX and trying to serialize them to GraphML for use in Gephi and graph-tool. Unfortunately the following error is really starting to get on my nerves:

```
networkx.exception.NetworkXError: GraphML writer does not support <class 'datetime.datetime'> as data values.
```

Also it doesn't support `<type NoneType>` or `list` or `dict` or ...

So I have to do something about it:

<script src="https://gist.github.com/bbengfort/52f6c13eaf5337d0fc1e46aad0bd9614.js"></script>

This is my first attempt, I'm simply going through all nodes and edges and directly updating/serializing their data values (note that Graph properties are missing). This pretty much makes the graph worthless after writing to disk. It also means that you have to do the deserialization after reading in the GraphML. There has to be a better way.
