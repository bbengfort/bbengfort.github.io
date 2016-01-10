---
layout: post
title:  "Simple CLI Script with Argparse"
date:   2016-01-10 14:48:14 -0500
categories: snippets
---

Let's face it, most of the Python programs we write are going to be used from the command line. There are _tons_ of command line interface helper libraries out there. My preferred CLI method is the style of Django's management utility. More on this later, when we hopefully publish a library that gives us that out of the box (we use it in many of our projects already).

Sometimes though, you just want a simple CLI script. These days we use the standard library `argparse` module to parse commands off the command line. Here is my basic script that I use for most of my projects:

<script src="https://gist.github.com/bbengfort/1884936b3a7efbf364f0.js"></script>

So how do you use this? Well essentially you just add subcommand parsers and their associated helper functions. Generally speaking you should do most of the work in the module and simply import that work to be executed here; only the command line context should be managed from your helper functions.
