---
categories: snippets
date: "2016-02-02T20:43:07Z"
title: On Interval Calls with Threading
---

Event driven programming can be a wonderful thing, particularly when the execution of your code is dependent on user input. It is for this reason that JavaScript and other user facing languages implement very strong event based semantics. Many times event driven semantics depends on elapsed time (e.g. wait then execute). Python, however, does not provide a native `setTimeout` or `setInterval` that will allow you to call a function after a specific amount of time, or to call a function again and again at a specific interval.

Consider a naive example where the program just waits a specific amount of time then calls a function:

```python
import time

def wait(delay, func):
    """
    Waits a certain amount of time, then calls func.
    """
    time.sleep(delay)
    func()
```

When this function is called it begins _blocking_ &mdash; that is the code cannot continue while we are in the delay. Therefore if you want to listen for user input, it won't be evaluated until after the delay is complete. This is bad.

In order to implement something that is _nonblocking_ in Python &mdash; that is it runs independently of the main execution of the code, we need to use the `threading` module. This is not a blog on threading, which is an enormous topic of its own. It should suffice to say for this blog post that the `threading` module allows us to spin off an independent thread that executes on its own while the main process continues. This will allow us to schedule functions to be called at a later date in a non blocking fashion.

The threading module has a helpful `threading.Timer` object that you can use to set a delay and run the function:

```python
import threading

def wait(delay, func):
    timer = threading.Timer(delay, func)
    timer.start()
```

You can cancel the timer, and even pass both positional and keyword arguments directly to the object. This gives us the ability to easily wait a delay then call the function. However, what if you want to run the function multiple times on an interval? The simple answer is have your function, when run, create a new timer object. However, your main thread then loses control of its hook to the timer object, which means that you can't cancel the interval (and your program will never terminate)! My method is personalized from an answer to the Stack Overflow question: &ldquo;[Run certain code every n seconds](http://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds)&rdquo; and is as follows:

<script src="https://gist.github.com/bbengfort/a7d46013f39cf367daa5.js"></script>

My special sauce is the use of `functools.partial` to create a closure and the `__call__` override, which allows me to actually _interrupt_ the interval and execute the function ahead of time, resetting the interval. As you can see, the elapsed time gets printed out every `n` seconds, without blocking the code waiting for user input (in this case, a `KeyboardInterrupt`).

So how might you use this in practice? Well, I originally was thinking about this to do lightweight routine memory sampling for a quick analysis. Adapting an answer to the Stack Overflow question: &ldquo;[How do I profile memory usage in Python?](http://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python)&rdquo;, I came up with the following wrapper for the `resource` module:

> Disclaimer: this is not the best method for memory profiling, there are definitely way better tools out there for this!

<script src="https://gist.github.com/bbengfort/63f3e14b3693d695ef8b.js"></script>

Here you can see that every 5 seconds, the memory usage is written to a CSV file, without interrupting the main code execution! Although this is a simple way to add a lot of rich features to your code; take care - the threading module can be tricky! Note that if you don't stop the interval, then your program won't stop! So make sure on exit you do the work of cleaning these things up! 
