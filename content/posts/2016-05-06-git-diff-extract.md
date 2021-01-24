---
aliases:
- /snippets/2016/05/06/git-diff-extract.html
categories: snippets
date: '2016-05-06T08:43:29Z'
draft: false
showtoc: false
slug: git-diff-extract
title: Extracting Diffs from Git with Python
---

One of the first steps to performing analysis of Git repositories is extracting the changes over time, e.g. the Git log. This seems like it should be a very simple thing to do, as visualizations on GitHub and elsewhere show file change analyses through history on a commit by commit basis. Moreover, by using the [GitPython](http://gitpython.readthedocs.io/en/stable/) library you have direct access to Git repositories that is scriptable. Unfortunately, things aren't as simple as that, so I present a snippet for extracting change information from a Repository.

First thing first, dependencies. To use this code you must install GitPython:

```
$ pip install gitpython
```

What I'm looking for in this example is the change for every single file throughout time for every commit. This doesn't necessarily mean the change in the blobs themselves, but metadata about the change that occurred. For example:

- Object: the path or name of the file
- Commit: the commit in which the file was changed
- Author: the username or email of the author of the file
- Timestamp: when the file was changed
- Size: the number of bytes changed (negative for deletions)
- Type of change: whether the file was added, deleted, modified, or renamed.
- Stats: the number of lines changed/inserted/deleted.

This pretty straight forward analysis will allow us to build a graph model of how users and files interact inside of a particular project. So here's the snippet:

{{< gist bbengfort 7a7e40930275f1d5633c3c59afc93f5d >}}

The result from this snippet is a generator that yields dictionaries that look something like:

```json
{
  "deletions": 0,
  "insertions": 18,
  "author": "benjamin@bengfort.com",
  "timestamp": "2016-02-23T12:36:59-0500",
  "object": "cloudscope/tests/test_utils/__init__.py",
  "lines": 18,
  "commit": "00c5dd71d86f94dce5fd31b254a1c690c5ec1a53",
  "type": "A",
  "size": 509
}
```

This can be used to create a history of file changes, or to create a graph of files that are commonly changed together.
