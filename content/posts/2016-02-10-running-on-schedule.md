---
aliases:
- /programmer/2016/02/10/running-on-schedule.html
categories: programmer
date: '2016-02-10T09:50:33Z'
draft: false
showtoc: false
slug: running-on-schedule
title: Running on Schedule
---

Automation with Python is a lovely thing, particularly for very repetitive or long running tasks; but unfortunately someone still has to press the button to make it go. It feels like there should be an easy way to set up a program such that it runs routinely, in the background, without much human intervention. Daemonized services are the route to go in server land; but how do you routinely schedule a process to run on your local computer, which may or may not be turned off<sup><small>[1](#ros-footnote-1)</small></sup>? Moreover, long running daemon processes seem expensive when you just want a quick job to execute routinely.

Let's consider the following use case: you're working on a data analysis project that requires the mashup of two different data sources. The first data source has to be ingested routinely, every hour, and the second has to be fetched sometime after, depending on the result of the first query. Obviously, you don't want to have to go to your computer and run your service, so your choices are:

- Let the OS run your program for you ([launchd](https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/launchd.8.html#//apple_ref/doc/man/8/launchd) or [cron](https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man8/cron.8.html#//apple_ref/doc/man/8/cron))
- Let an external daemon service run your program ([celery](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html) or [luigi](https://github.com/spotify/luigi))
- Create a long running program that mostly sleeps ([schedule](https://github.com/dbader/schedule) or [sched](https://docs.python.org/2/library/sched.html))

Frankly, these aren't great choices, but they're the best we've got. In this post, I will explore the first and third options in a bit more detail. The second option is the more services-oriented route that you might expect to see on servers rather than on your local machine. I will probably discuss those options in other posts, as I start to use them more frequently in my work.

## The Infamous Cron

There are actually many versions of `cron`, which was originally studied in the late 1970's in parallel with research concerning discrete event simulation. The modern version that is typically used is Vixie or ISC cron, named after its original programmer, Paul Vixie who wrote it in 1987. Because of its rich history, maturity, and standard inclusion with most Linux distros, `cron` is the defacto tool for scheduling periodic tasks in the background.

`cron` is a Linux/Unix utility which allows users to execute commands automatically at a specified time and date or periodically on a schedule. While technically `cron` is a daemon service that is launched when the OS boots, because it is available preinstalled on almost all Linux/Unix systems I believe it is legitimate to talk about it being a part of the operating system. However, it is important to check that the `crond` daemon is running on your computer, otherwise your scheduled command won't execute.

### Cron Voodoo

Working with `cron` means editing `crontab` (cron configuration) files. System wide jobs can be installed by modifying `/etc/crontab`, however users should use the `crontab` tool if available to create local jobs. The `crontab` files can contain variables that modify how `cron` is used, but the most important part are the entry lines that describe when and what to execute. Consider that we have a file called `ingest.py`, which is installed on the path, in order to run that every five minutes, we would write an entry similar to the following:

```
0-59/5 * * * *  $HOME/bin/ingest.py >> $HOME/log/ingest.out 2>&1
```

There are two parts to the voodoo of this entry, the schedule and the command. The schedule has five fields: minute, hour, day of month, month, day of week. By specifying a single number, you specify exactly when to run the job. For example to run a job on the first of April at 8:15 AM:

```
15 8 1 4 *  echo "April Fools!"
```

The `*` stands for &ldquo;first-last&rdquo; a short cut for the maximum range. In our first example we used `0-59` to specify that we wanted it to run every minute between the 0th minute and the 59th minute. We could have replaced this with `*` to shorten the syntax. The `/` allows us to specify a step, therefore in our example `*/5` means run every five minutes.

The second part is our command. In the ingest example we execute a Python file (which should have a `#!/usr/bin/env python` at the top of it and have executable permissions) that is in our home directory, in the `bin` folder. We then append the output to a log file, and redirect the standard error pipe to standard out (so that we can have one log file). It is important to understand where your output is going in order to debug errors and capture messages that are printed to the command line!

### OS X Launchd

If you're working on OS X, the preferred method for creating periodic or timed jobs is to use `launchd`, though `cron` is technically available<sup><small>[2](#ros-footnote-2)</small></sup>. Every `launchd` job is specified by property list (plist) file in XML format, therefore instead of maintaining a single `crontab` file with all entries, managing `launchd` jobs is as simple as adding and removing .plist files!

Configuring `launchd` plist files is more expressive than `crontab`, and allows you to include a lot of information about your background process; for more information see [Creating a launchd Property List File](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html#//apple_ref/doc/uid/TP40001762-104142). There are four properties that must be included with each configuration: `Label` to identify your job, `ProgramArguments` used to launch your job, `inetdCompatibility` which is specifically for servers, and `KeepAlive` which specifies if your job launches on demand or must always be running. Our 5 minute `ingest.py` command is specified as follows:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.districtdatalabs.ingest</string>

    <key>ProgramArguments</key>
    <array>
        <string>$HOME/bin/ingest.py</string>
    </array>

    <key>StandardOutPath</key>
    <string>$HOME/log/ingest.out</string>

    <key>StandardErrorPath</key>
    <string>$HOME/log/ingest.out</string>

    <key>StartInterval</key>
    <integer>300</integer>
</dict>
</plist>
```

Although a bit more verbose, `launchd` configuration gives a bit more flexibility and a bit more readability about what is happening. You can also specify calendar based intervals, or even modify a directory to detect if paths have been changed. After creating the plist file for your ingest command, install it to `/Library/LaunchAgents` or in the `LaunchAgents` directory of the user specific `Library` folder. If you don't want to specify the entire path to the executable, you can symlink ingest.py to `/usr/local/libexec` as follows:

```
$ ln -s $HOME/bin/ingest.py /usr/local/libexec/ingest.py
```

> On OS X, the term &ldquo;daemon&rdquo; is used to specify system-level background processes, where the term &ldquo;agent&rdquo; is used to specify per-user background processes<sup><small>[3](#ros-footnote-3)</small></sup>. Note that an agent will not run if its assigned user is not logged in. Similarly by installing a `launchd` plist to `/Library/LaunchDaemons`, the service will run at the  system level.

### Is the Computer On?

For OS X, if your system is off or asleep, `cron` jobs will not execute, and will run when the next scheduled time occurs and the computer is turned back on. Similarly, most `launchd` jobs are skipped if the computer is off or asleep as well. However, if a `launchd` job is specified by the `StartCalendarInterval` key, and the computer is asleep when the job should have run, it will run when the computer wakes up. This doesn't count if the computer is off, however.

It is important to keep in mind when your computer is on and running, and how it might affect your background services. If the computer is always off or asleep at the job's scheduled time, then it will never run.

## Scheduling and Waiting

While `cron` and `launchd` are great for scheduling jobs that run periodically, it does have some issues<sup><small>[4](#ros-footnote-4)</small></sup>. For example, `cron` is a per-machine configuration, not an application configuration, which makes it difficult to scale the number of machines that are working together. Both `cron` and `launchd` are also difficult to debug and finally, bigger problems can be designed with tools like queues and workers that are easier to work with but not suitable for scheduling with `cron`.

The bottom line is that as your program gets more complex, it's better to turn it into a long-running service or daemon with its own built-in scheduler than to let the OS run it every once in a while. Note you'll still use `launchd` to ensure that the daemon is running in the background, or something like `upstart` on Linux. In this section we'll look at a program that creates its own delays using the standard library `sched` and third party `schedule` utilities.

### Python Event Scheduler

The standard library `sched` module defines a `scheduler` class that implements general purpose periodic events and callbacks for _single process_ Python programs. The `scheduler` requires two functions to actually handle the scheduling: a `timefunc`, which should be a callable without arguments that returns a number that represents the current time and a `delayfunc` which should accept one argument compatible with the output of the `timefunc` and should delay that many units. The simplest implementation of our ingest function is as follows:

```python
#!/usr/bin/env python
import sched, time
from ingest import ingest

scheduler = sched.scheduler(time.time, time.sleep)

def ingestion_runner(*args, **kwargs):
    """
    Runs ingestion every 5 minutes for an hour.
    """
    # Pass arguments to ingest function
    doingest = lambda: ingest(*args, **kwargs)

    # Set the scheduler to run doingest
    for interval in xrange(0, 60, 5):
        scheduler.enter(interval*60, 1, doingest, ())

    # Run the scheduler
    print "Ingestion started at {}".format(time.time)
    scheduler.run()
    print "Ingestion finished at {}".format(time.time)

if __name__ == '__main__':
    ingestion_runner()
```

This style of scheduler basically allows you to create a chain of events ahead of time using the `enter` method. Then when the scheduler is run, it simply calls `time.sleep` for the number of seconds before its next scheduled event, executes that event, and then sleeps until the next event. The `sched` module is really nice to create a complex sequence of events, so that you don't have to do the math about sleeping in between. However, once the schedule is running, it is completely blocking (because of the sleep call), and your program won't be able to do anything (not even catch signals like `KeyboardInterrupt`) until the next event occurs.

### Schedule API

As an alternative to the standard library `sched`, the third party `schedule` library allows you to build an in-process scheduler for periodic jobs, without necessarily blocking. Schedule is designed as a lightweight API that runs a callable and pre-determined intervals, and has the most friendly syntax of any of the tools we've discussed so far. To use `schedule`, install it with `pip`:

```
$ pip install schedule
```

We can then convert our ingestion runner from above into something a lot less verbose, and which will allow us to sleep on our own terms, and exit if we want to. The `schedule` ingestion runner is as follows:

```python
#!/usr/bin/env python
import sys
import time
import schedule

from ingest import ingest
from functools import partial

def ingestion_runner(*args, **kwargs):
    """
    Runs the ingest function with the given arguments every 5 minutes.
    """
    # Use partial based method instead of lambda
    doingest = partial(ingest, *args, **kwargs)

    # Set the scheduler to do ingest.
    schedule.every(5).minutes.do(doingest)

    # Run the scheduler, with the ability to cancel early
    counter = 0
    while True:
        try:
            schedule.run_pending()
            counter += 1
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break

    print "Ran ingest {} times".format(counter)
    sys.exit(0)

if __name__ == '__main__':
    ingestion_runner()
```

The `schedule` api allows us to only block 1 second at a time, which gives us the opportunity to check if someone is trying to exit. Moreover, we don't have to specify or compute exactly when to schedule our job; the `every` method just keeps the job running as long as we want!

## Conclusion

In the context of data science, we're used to saying that we can create automated platforms for performing ingestion, wrangling, model building, etc. However, outside the context of a web application, sometimes it is not clear how to get these tools up and running in an automated fashion. I hope this post presents a _simple_ method for getting routine jobs going on your machine, and that it will enable you to ingest enough data to perform high quality analytics. At the very least, it should serve as a reference to point you towards the tools that you need to know.

This post is the first in a series where I discuss &ldquo;software immortality: daemons, schedulers, and programs that live forever&rdquo;. I hope to continue this discussion with task queues and workers, discuss Celery and other Python projects that let comptuers do a lot of work on your behalf. 

### Footnotes

<a name="ros-footnote-1">1.</a> Stack Overflow asks: [How do I get a Cron like scheduler in Python](http://stackoverflow.com/questions/373335/how-do-i-get-a-cron-like-scheduler-in-python)

<a name="ros-footnote-2">2.</a> Mac OS X Daemons and Services: [Scheduling Timed Jobs](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html).

<a name="ros-footnote-3">3.</a> See [Daemons and Agents](https://developer.apple.com/library/mac/technotes/tn2083/_index.html#//apple_ref/doc/uid/DTS10003794) from the Apple Developer Library for more.

<a name="ros-footnote-4">4.</a> Schedule was inspired by Adam Wiggins' article, [Rethinking Cron](http://adam.herokuapp.com/past/2010/4/13/rethinking_cron/).
