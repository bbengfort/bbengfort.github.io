---
layout: post
title:  "Frequently Copied and Pasted"
date:   2016-01-08 23:14:57 -0500
categories: programmer
---

I have a bit of catch up to do &mdash; and I think that this notepad and development journal is the perfect resource to do it. You see, I am _constantly_ copy and pasting code from other projects into the current project that I'm working on. Usually this takes the form of a problem that I had solved previously that has a similar domain to a new problem, but requires a slight amount of tweaking. Other times I am just doing the same task over and over again.

> &ldquo;But Ben, if you're repeating yourself, shouldn't you just make an open source module, require it as a dependency and import it?&rdquo;

Says you, whose voice sounds strangely like that of [@looselycoupled](https://github.com/looselycoupled). Well of course I should, but the problem is that takes _time_ &mdash; how much of that do you think I have? I've tried to get a `benlib` going in the past; but upkeep is tough. And anyway I have done that. The prime example is [confire](https://github.com/bbengfort/confire), because we kept using the same YAML configuration code over and over again.

In fact there are two massive pieces of code that need to be made into a library, if only for our own sanity:

1. **console utilities**: we like to wrap `argparse` into a Django-like command program. Then all we have to do is write `Command` subclasses and they're automatically added to our application. This needs to be a library ASAP. While we're at it, we may as well stick our `WrappedLogger` utility in as well.

2. **sql query (ormbad)**: ORMs are such a pain, especially if you're good at SQL (we are). We constantly write this `Query` class to wrap our SQL and load them from disk, etc. In fairness, we actually have started the dependency: [ormbad](https://github.com/tipsybear/ormbad), but we need to finish it.

However, there is also a whole host of stuff that we use in our utilities, like the famous `Timer` class that we got from (somewhere?) and use _all the time_.

<script src="https://gist.github.com/bbengfort/bd5be18d00c9e982a032.js"></script>

But you know, hunting for Gists is hard, hunting for code in other repositories is hard. So you know what? I'm just going to put it all here. Quick and dirty in the hopes that I'll have a one stop shop for copy and paste. Plus embedding those Gists is very, very handy.
