---
categories: snippets
date: "2016-08-01T12:17:47Z"
title: Pretty Print Directories
---

It feels like there are many questions like this one on Stack Overflow: [Representing Directory & File Structure in Markdown Syntax](http://stackoverflow.com/questions/19699059/representing-directory-file-structure-in-markdown-syntax), basically asking "how can we represent a directory structure in text in a pleasant way?" I too use these types of text representations in slides, blog posts, books, etc. It would be very helpful if I had an automatic way of doing this so I didn't have to create it from scratch.

Of course, many tools do this; and it should be pretty easy to write a Python script to do this exactly the way you want to. So, I did. The Script in Gist form is below. My suggestion is to download this file, stick it into your path, and change it's permissions to be executable. You can do this as follows:

```
$ mkdir ~/bin/
$ curl -o ~/bin/pdir http://bit.ly/2aDnXtj
$ chmod +x ~/bin/pdir
```

This assumes that your `~/bin` directory is on your path (which it usually is on Unix systems). Then usage is as simple as:

```
$ pdir path/to/dir/to/print
```

For example, the website for this blog looks like this:

```
bbengfort.github.io/_site/
├── 404.html
├── Gemfile
├── Gemfile.lock
├── LICENSE
├── README.md
├── about.html
├── archive.html
└── assets
|   ├── 2016-06-23-graph-tool-viz.png
|   ├── apple-touch-icon-precomposed.png
|   └── css
|   |   ├── hyde.css
|   |   ├── libelli.css
|   |   ├── poole.css
|   |   └── syntax.css
|   └── data
|   |   ├── pi-10k.txt
|   |   └── timestepping.csv
|   ├── favicon.ico
|   ├── icon.png
|   └── images
|   |   ├── 2016-01-28-timeline.svg
|   |   ├── 2016-02-16-observer.png
|   |   ├── 2016-03-04-pi-grid.png
|   |   ├── 2016-03-14-matplotlib-segfault.png
|   |   ├── 2016-03-14-pi-grid.png
|   |   ├── 2016-04-15-interact-plot.png
|   |   ├── 2016-04-15-timestepping.png
|   |   ├── 2016-04-19-ml-data-management-workflow.png
|   |   ├── 2016-04-26-cloudscope-consistency-visualization.png
|   |   ├── 2016-04-26-epaxos-message-flow.png
|   |   ├── 2016-04-26-raft-message-flow.png
|   |   ├── 2016-04-26-raftscope-replay-visualization.png
|   |   ├── 2016-04-26-secret-lives-of-data-raft-visualization.png
|   |   ├── 2016-05-10-mora-architecture.png
|   |   ├── 2016-05-19-nltk-sklearn-text-pipeline.png
|   |   ├── 2016-06-23-graph-tool-viz.png
|   |   ├── 2016-06-27-big-sigma-curve.png
|   |   └── 2016-06-27-small-sigma-curve.png
├── feed.xml
├── index.html
└── observations
|   └── 2016
|   |   └── 04
|   |   |   └── 15
|   |   |   |   └── lessons-in-discrete-event-simulation.html
|   |   |   └── 26
|   |   |   |   └── visualizing-distributed-systems.html
... [snip] ...
```

Ok, that's a lot, so it was snipped for brevity, but you get the picture: here's the code:

<script src="https://gist.github.com/bbengfort/81c4766a46c9ad2ec847473b1ce6678d.js"></script>


Enjoy this code snippet brought to you by procrastination and coffee; also me skipping lunch. 
