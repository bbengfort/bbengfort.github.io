---
aliases:
- /snippets/2020/11/24/mac-cleanup.html
categories: snippets
date: '2020-11-24T14:26:25Z'
draft: false
showtoc: false
slug: mac-cleanup
title: OS X Cleanup
---

Developer computers often get a lot of cruft built up in non-standard places because of compiled binaries, assets, packages, and other tools that we install over time then forget about as we move onto other projects. In general, I like to reinstall my OS and wipe my disk every year or so to prevent crud from accumulating. As an interemediate step, this post compiles several maintenance caommands that I run fairly routinely.

## Homebrew

Update homebrew and remove old formulae and their folders often, otherwise it's going to take a long time to run if you forget about it!

```
$ brew update
$ brew upgrade
$ brew cleanup
```

Linking and casks are also often problems, run `brew doctor` to inspect the warnings and take care of anything that needs cleaning up. Note that I usually run update and upgrade multiple times to make sure everything was correctly grabbed.

Finally, a routine `brew list` will show what has been installed; although it's tough to figure out dependencies from brew, if I recognize something that I installed and am not using anymore, I usually uninstall it.

## Docker

I fairly routinely clean up docker containers, images, volumes, networks, etc. from my machine since I don't generally rely on a local build process except for testing.

```
$ docker system prune --all
```

## Python

I manage my Python system and environments with `pyenv`, which means it's easy to build up a cruft of old environments and duplicate copies of Python packages. Using `pyenv versions`, list your environments and versions routinely and then use either `pyenv uninstall` to remove a version of Python or `pyenv virtualenv-delete` to remove a virtual environment.

## Ruby

I don't use Ruby very much, but similar to Python I have `rbenv` for a few projects that require Ruby components. Use `rbenv versions` to list Ruby installs and then `rbenv uninstall` to remove the environments.

Also routinely run:

```
$ gem cleanup --dryrun
$ gem cleanup
```

To clean up old versions of gems.

## Node Modules

Node and `npm` download a lot of packages into project directories. The following command searches for any `node_modules` directories that are older than 4 months.

```
$ find . -name "node_modules" -mtime +120 -type d
```

Clean them up as follows:

```
find . -name "node_modules" -mtime +120 -type d | xargs rm -rf
```

I usually run this in my workspaces directory before I engage in any web development.

## Git

I usually do a pretty good job deleting branches that have been merged from my local computer, but ocassionally I'll clone a repository and do a fetch that pulls down a bunch of branches. The following command says what branches have been merged:

```
$ get branch --merged main
```

The issue with this is that we normally squash and merge our branches, so this may not catch the branches you're looking for. However, thinking about how many git objects are on your system is important!