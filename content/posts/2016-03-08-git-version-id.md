---
categories: snippets
date: "2016-03-08T13:57:56Z"
title: Adding a Git Commit to Header Comments
---

You may have seen the following type of header at the top of my source code:

```python
# main
# short description
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Mar 08 14:07:24 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: main.py [] benjamin@bengfort.com $
```

All of this is pretty self explanatory with the exception of the final line. This final line is a throw back to Subversion actually, when you could add a `$Id$` tag to your code, and Subversion would [automatically populate](http://www.startupcto.com/server-tech/subversion/setting-the-id-tag) it with something that looks like:

```
$Id: test.php 110 2009-04-28 05:20:41Z dordal $
```

This was pretty cool for tracking who did what in files and for specifically finding the correct version of changes. Back when I first started programming, I used Mercurial for revision control, and we had a pre-commit hook that would automatically populate our files with this line and the first seven characters of the SHA-1 hash for the commit. This line has remained in my code banner ever since, even when I switched to Git, and as a result, much of my code doesn't have this ID!

The problem is that this really only works in a centralized version control system - because you know what the next commit will be before you do it. In a decentralized VCS like Git (and Mercurial for that matter), the commit identity is not known until after commit and merge. Moreover, if you change the file in place in a pre-commit hook in Git, then the staging index is modified and the hash changes. It's definitely not very easy.

Still, I really wanted to populate these tags with _something_ - so instead of adding the revision that the file was _modified_, I changed it to the revision that the file was _created_. At the very least now you can look at the file and go to the revision in GitHub and follow the changes to the file through revisions. So I came up with the following:

<script src="https://gist.github.com/bbengfort/d747ea6806366c21cd34.js"></script>

The first problem was reading the commits from the local repository. I added the [gitpython](https://github.com/gitpython-developers/GitPython) dependency so I would have access to Git from Python. Trust me, it was _not_ easy to figure out how to create a simple mapping of paths in the repository to commit objects. As you can see in the snippet, I finally figured out I could simply iterate through all the commits, then traverse the tree of that commit. Because the `iter_commits` goes _backward_ through commit history, it has the effect that the file's creation commit is the last stored in the dictionary. This is, however, at the cost of having to iterate through _every_ tree of _every_ commit to get the mapping. I tried using diffs and other tools, but they wouldn't do exactly what I wanted.

Now as you can see in the [Baleen](https://github.com/bbengfort/baleen) repository, the files all have version information tagged in their headers as follows:

```python
# ID: opml.py [b2f890b] benjamin@bengfort.com $
```

Is it perfect? No, I'd still like to have latest commits, but if I commit the files with the new header, then that will be the latest commit, and that's definitely not the effect I want. To really get detailed I'd have to check the diff to see if it was only the line it changed, and that seems like too much work. However, now at least my ID lines have something meaningful in them, so that's nice. 
