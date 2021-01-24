---
aliases:
- /snippets/2017/01/23/syscall-errno.html
categories: snippets
date: '2017-01-23T14:29:50Z'
draft: false
showtoc: false
slug: syscall-errno
title: Error Descriptions for System Calls
---

Working with [FUSE](https://bazil.org/fuse/) to build file systems means inevitably you have to deal with (or return) system call errors. The [Go FUSE](https://godoc.org/bazil.org/fuse#pkg-constants) implementation includes helpers and constants for returning these errors, but simply wraps them around the [syscall](https://golang.org/pkg/syscall/#pkg-constants) error numbers. I needed descriptions to better understand what was doing what. Pete saved the day by pointing me towards the `errno.h` header file on my Macbook. Some Python later and we had the descriptions:

{{< gist bbengfort c994bd1fdc03bd5f55f4db78eaad5edd >}}

So that's a good script to have on your local machine, since now I can just do the following:

```
$ syserr.py | grep EAGAIN
 35: EAGAIN: Resource temporarily unavailable
```

To get descriptions for the various errors. However for Google reference, I'll also provide them here:

{{< gist bbengfort cb0f999284a42ee993bb8cbdc1e0dfec >}}

End of post.
