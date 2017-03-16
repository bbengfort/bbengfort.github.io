---
layout: post
title:  "Pseudo Merkle Tree"
date:   2017-03-16 12:23:21 -0400
categories: snippets
---

A [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree) is a data structure in which every non-leaf node is labeled with the hash of its child nodes. This makes them particular useful for comparing large data structures quickly and efficiently. Given trees `a` and `b`, if the root hash of either is different, it means that part of the tree below is different (if they are identical, they are probably also identical). You can then proceed in a a breadth first fashion, pruning nodes with identical hashes to directly identify the differences.

These structures are widely used with file systems or directory trees, for example, Git uses them to identify the file tree structure of a commit so that two commits can be compared easily even for extremely large directory tree structures. Files are leaf nodes, identified by the hash of their contents. Directories are the non-terminal nodes (and this is part of the reason that Git doesn't track directories). The hash of a directory is the hash of the hashes of the files and directories that make up that node's children.  

The trade-off for fast comparison is that a Merkle tree is time consuming to build and to maintain. Adding a file means computing the hash of the file, then recomputing the hash of the directory that the file is in, then recomputing the hash of that directory's parent and so on to the root. Generally speaking hash computations are expensive, particularly ones that decrease the likelihood of collisions (e.g. something stronger than MD5).

A simpler data structure that may do the same thing is one that maintains counts of the leaf nodes under it. Instead of computing hashes, the computational work is to simply increment the counter as files are added, all the way to the root node. I can't imagine this type of tree doesn't already exist, and it does suffer from several problems. First, and most harmfully, if the same number of files are added to both trees then the counts will be the same and the trees declared identical. Additionally, if the contents of the files change, this type of tree won't be updated. However, for some applications, particularly those that simply need to identify if changes are occurring with a high likelihood, this structure can be effective.  

The code is as follows:

<script src="https://gist.github.com/bbengfort/4215db0bd29186615975b4f0e6c96c38.js"></script>

In principle the API is fairly thread-safe. Simply initialize a `Tree` with the `Build` function by supplying a path. The `Tree` will walk the directory and construct child directories and increment the counts of files. It uses the `AddFile` method to do this, which locks the tree at the root node, and updates it in a top-down fashion. I say "fairly thread-safe" because child nodes are not locked as they're being updated, nor is the tree locked on `AddChild`. So long as the user interacts only with the root node and the `AddFile` function (the principle use) then it can be used concurrently. 
