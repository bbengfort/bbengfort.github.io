---
aliases:
- /snippets/2017/07/11/pid-management.html
categories: snippets
date: '2017-07-11T09:10:44Z'
draft: false
showtoc: false
slug: pid-management
title: PID File Management
---

In this discussion, I want to propose some code to perform PID file management in a Go program. When a program is backgrounded or daemonized we need some way to communicate with it in order to stop it. All active processes are assigned a [unique process id](https://en.wikipedia.org/wiki/Process_identifier) by the operating system and that ID can be used to send signals to the program. Therefore a PID file:

> The pid files contains the process id (a number) of a given program. For example, Apache HTTPD may write it's main process number to a pid file - which is a regular text file, nothing more than that - and later use the information there contained to stop itself. You can also use that information (just do a `cat filename.pid`) to kill the process yourself, using `echo filename.pid | xargs kill`.
>
> &mdash; [Rafael Steil](https://stackoverflow.com/questions/8296170/what-is-a-pid-file-and-what-does-it-contain)

From a Go program we can use the PID to get access to the program and send a signal, such as `SIGTERM` - terminate the program!

```go
import (
	"os"
	"syscall"

	"github.com/bbengfort/x/pid"
	"github.com/urfave/cli"
)

// Send a kill signal to the process defined by the PID
func stop(c *cli.Context) error {
	pid := pid.New()
	if err := pid.Load(); err != nil {
		return cli.NewExitError(err.Error(), 1)
	}

	// Get the process from the os
	proc, err := os.FindProcess(pid.PID)
	if err != nil {
		return cli.NewExitError(err.Error(), 1)
	}

	// Kill the process
	if err := proc.Signal(syscall.SIGTERM); err != nil {
		return cli.NewExitError(err.Error(), 1)
	}

	return nil
}
```

Using the PID file within a program requires a bit of forethought. Where do you store the PID file? Do you only allow one running instance of the program? If so, the program needs to throw an error if it starts up and a PID file exists, if not, how do you name multiple PID files? When exiting, how do you make sure that the PID file is deleted?

Some of these questions are addressed by my initial implementation of the PID file in the [github.com/bbengfort/x/pid](https://godoc.org/github.com/bbengfort/x/pid) package. The stub of that implementation is as follows:

{{< gist bbengfort 9120ee6ba5ee5badda578f2072e17c5a >}}

This implementation stores both the PID and the parent PID (if the process forks) in the PID file in JSON format. JSON is not necessarily required, but it does make the format a bit simpler to understand and also allows the addition of other process information.

So why talk about PIDs? Well I'm writing some programs that need to be run in the background and always started up. I'm investigating [systemd](https://wiki.ubuntu.com/SystemdForUpstartUsers) for Ubuntu and [launchtl](http://www.launchd.info/) for OS X in order to manage the processes. But more on that in a future post.
