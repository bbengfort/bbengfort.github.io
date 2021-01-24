---
categories: snippets
date: "2017-06-12T16:04:24Z"
title: Appending Results to a File
---

In my current experimental setup, each process is a single instance of sample, from start to finish. This means that I need to aggregate results across multiple process runs that are running concurrently. Moreover, I may need to aggregate those results between machines.

The most compact format to store results in is CSV. This was my first approach and it had some benefits including:

1. small file sizes
2. readability
3. CSV files can just be concatenated together

The problems were:

1. headers become very difficult
2. everything is a string, no int or float types without parsing

The headers problem is really the biggest problem, since I need future me to be able to read the results files and understand what's going on in them. I therefore opted instead for [.jsonl](http://jsonlines.org/) format, where each object is newline delimited JSON. Though way more verbose a format than CSV, it does preclude the headers problem and allows me to aggregate different results versions with ease. Again, I can just concatenate the results from different files together.

This is becoming so common in my Go code, here is a simple function that takes a path to append to as input as well as the JSON value (the interface) and appends the marshaled data to disk:

<script src="https://gist.github.com/bbengfort/4c7a46540bf89aced9b8864d884d0b4c.js"></script>

Now my current worry is atomic appends from multiple processes (is this possible?!) I was hoping that the file system would lock the file between writes, but I'm not sure it does: [Is file append atomic in UNIX?](https://stackoverflow.com/questions/1154446/is-file-append-atomic-in-unix). Anyway, more on that later.
