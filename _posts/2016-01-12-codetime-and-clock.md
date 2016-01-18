---
layout: post
title:  "The codetime and clock Commands"
date:   2016-01-12 17:02:51 -0500
categories: snippets
---

If you've pair programmed with me, you might have seen me type something to the following effect on my terminal, particularly if I have just created a new file:

    $ codetime

Then somehow I can magically paste a formatted timestamp into the file! Well it's not a mystery, in fact, it's just a simple alias:

```bash
alias codetime="clock.py code | pbcopy"
```

Oh, well that's easy &mdash; why the blog post? Hey, what's `clock.py`? A great question! This Python script is the _dumbest_ thing that I have ever written, that has become the most _useful_ tool that I use on a daily basis. Whenever there is a dumb to useful ratio like that, it's blogging time. Here is `clock.py`:

<script src="https://gist.github.com/bbengfort/810d5fb2e5d4c839a1c1.js"></script>

So that's it. It literally just prints out a string formatted `datetime` based on a named argument like "code". In fact, this Jekyll blog has a date property in the YAML front matter that I can get using `clock.py blog`! So why do this? Well first, I was tired of aliasing `date`, particularly because there is a [different implementation on OS X and Linux](http://stackoverflow.com/questions/9804966/date-command-does-not-follow-linux-specifications-mac-os-x-lion). Secondly, I needed JSON timestamps in UTC rather than my current time. This simple printer does that for me! So voila!  
