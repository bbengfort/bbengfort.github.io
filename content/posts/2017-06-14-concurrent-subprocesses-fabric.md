---
aliases:
- /snippets/2017/06/14/concurrent-subprocesses-fabric.html
categories: snippets
date: '2017-06-14T15:56:24Z'
draft: false
showtoc: false
slug: concurrent-subprocesses-fabric
title: Concurrent Subprocesses and Fabric
---

I've ben using [Fabric](http://docs.fabfile.org/) to concurrently start multiple processes on several machines. These processes have to run at the same time (since they are experimental processes and are interacting with each other) and shut down at more or less the same time so that I can collect results and immediately execute the next sample in the experiment. However, I was having a some difficulties directly using Fabric:

1. Fabric can parallelize one task across multiple hosts accordint to roles.
2. Fabric can be hacked to run multiple tasks on multiple hosts by setting `env.dedupe_hosts = False`
3. Fabric can only parallelize one type of task, not multiple types
4. Fabric can't handle large numbers of SSH connections

In this post we'll explore my approach with Fabric and my current solution.

## Fabric

Consider the following problem: I want to run a Honu replica server on four different hosts. This is pretty easy using fabric as follows:

```python
from itertools import count
from fabric.api import env, parallel, run

# assign unique pids to servers
counter = count(1,1)

# Set the hosts environment
env.hosts = ['user@hostA:22', 'user@hostB:22', 'user@hostC:22', 'user@hostD:22']

@parallel
def serve(pid=None):
    pid = pid or next(counter)
    run("honu serve -i {}".format(pid))
```

Note that this uses a global variable, `counter` to assign a unique id to each process (more on this later). What if I want to run four replica processes on four hosts? We can hack that as follows:

```python
from fabric.api import execute, settings


def multiexecute(task, n, host, *args, **kwargs):
    """
    Execute the task n times on the specified host. If the task is parallel
    then this will be parallel as well. All other args are passed to execute.
    """
    # Do nothing if n is zero or less
    if n < 1: return

    # Return one execution of the task with the given host
    if n == 1:
        return execute(task, host=host, *args, **kwargs)

    # Otherwise create a lists of hosts, don't dedupe them, and execute
    hosts = [host]*n
    with settings(dedupe_hosts=False):
        execute(task, hosts=hosts, *args, **kwargs)


# Note the removal of the decorator
def serve(pid=None):
    pid = pid or next(counter)
    run("honu serve -i {}".format(pid))


@parallel
def serveall():
    multiexecute(serve, 4, env.host)
```

Here, we create a `multiexecute()` function that temporarily sets `dedupe_hosts=False` using the `settings` context manager, then creates a host list that duplicates the original host `n` times, executing the task in parallel. By parallelizing the `serveall` task, each host is passed into the task once, then branched out 4 times by multiexecute.

Now, what if I want to run 4 `serve()` and 4 `work()` tasks with different arguments to each in parallel? Well, here's where things fall apart, it can't be done. If we write:

```python
@parallel
def serveall():
    multiexecute(serve, 4, env.host)
    multiexecute(work, 4, env.host)
```

Then the second `multiexecute()` will happen sequentially after the first `multiexecute()`. Unfortunately there seems to be no solution. Moreover, each of the additional tasks opens up a new SSH connection and many SSH connections quickly become untenable as you reach file descriptor limits in Python.

## Concurrent Subprocess

Ok, so let's step back - Fabric is great for one task to one host, let's continue to use that to our advantage. What can we put on each host that will be able to spawn multiple processes of different types? My first thought was a custom script, but after a tiny bit of research I found a StackOverflow question: [Python subprocess in parallel](https://stackoverflow.com/questions/9743838/python-subprocess-in-parallel).

The long and short of this is that creating a list of `subprocess.Popen` objects allows them to run concurrently. By polling them to see if they're done and using `select` to buffer IO across multiple processes, you can collect stdout on demand, managing the execution of multiple subprocesses.

So now the plan is:

1. Fabric sends a list of commands per host to pproc
2. pproc coordinates the execution of processes per host
3. pproc sends Fabric serialized stdout
4. Fabric quits when pproc exits

I've created a [command line script called pproc.py](https://gist.github.com/bbengfort/6b66fceb73dff58edd21e49967c0a07f) that wraps this and takes any number of commands and their arguments (so long as they are surrounded by quotes) and executes the `pproc` functionality described above. Consider the following "child process":

```python
#!/usr/bin/env python3

import os
import sys
import time
import random
import argparse

def fprint(s):
    """
    Performs a flush after print and prepends the pid.
    """
    msg = "proc {}: {}".format(os.getpid(), s)
    print(msg)
    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=5)
    args = parser.parse_args()

    for idx in range(5):
        worked = random.random() * args.limit
        time.sleep(worked)
        fprint("task {} lasted {:0.2f} seconds".format(idx, worked))

```

This script is just simulating work by sleeping, but crucially, takes an argument on the command line. If we run `proc` as follows:

```
$ pproc "./child.py -l 5" "./child.py -l 6" "./child.py -l 4"
```

Then we get the following serialized output:

```
proc 46145: task 0 lasted 2.68 seconds
proc 46146: task 0 lasted 3.13 seconds
proc 46145: task 1 lasted 0.95 seconds
proc 46144: task 0 lasted 3.70 seconds
proc 46144: task 1 lasted 0.15 seconds
proc 46146: task 1 lasted 1.12 seconds
proc 46145: task 2 lasted 2.90 seconds
proc 46146: task 2 lasted 2.80 seconds
proc 46144: task 2 lasted 3.67 seconds
proc 46146: task 3 lasted 0.59 seconds
proc 46144: task 3 lasted 2.30 seconds
proc 46146: task 4 lasted 2.23 seconds
proc 46145: task 3 lasted 4.65 seconds
proc 46144: task 4 lasted 3.06 seconds
proc 46145: task 4 lasted 4.05 seconds
```

Sweet! Things are happening concurrently and we can specify any arbitrary commands with their arguments on the command line! Win! The complete listing of the pproc script is as follows:

{{< gist bbengfort 6b66fceb73dff58edd21e49967c0a07f >}}

## Experiments

So what was this all for? Well, I'm running distributed systems experiments, and it's very tricky to coordinate everything and get results. A datapoint for an experiment runs the entire system with a specific workload and a specific configuration for a fixed amount of time, then dumps the numbers to disk.

Problem: For a single datapoint I need to concurrently startup 48 processes: 24 replicas and 24 workload generators on 4 machines. Each process requires a slightly different configuration. An experiment is composed of multiple data points, usually between 40-200 individual runs of samples that take approximately 45 - 480 seconds each.

The solutions I had proposed were as follows:

_Solution 1 (by hand)_: open up 48 terminals and type simultaneously into them using iTerm. Each configuration is handled by the environment of each terminal session. Experiments take about 4-5 hours using this method and is prone to user error.

_Solution 2 (ssh push)_: use fabric to parallelize the opening of 48 ssh sessions and run a command on the remote host. Experiment run times go down to about 1.5 hours, but each script has to be written by hand and am also noticing SSH failures for too many connections at the higher levels, it's also pretty hacky.

_Solution 3 (amqp pull)_: write a daemon on all machines that listens to an amqp service (AWS SQS is $0.40 for 1M requests) and starts up processes on the local machine. This would solve the coordination issue and could even aggregate results, but would require extra coding and involve another process running on the machines.

The solution described in this post would hopefully modify Solution 2 (ssh push) to actually make it tenable.
