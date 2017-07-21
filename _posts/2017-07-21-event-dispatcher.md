---
layout: post
title:  "Event Dispatcher in Go"
date:   2017-07-21 06:28:45 -0400
categories: snippets
---

The event dispatcher pattern is extremely common in software design, particularly in languages like JavaScript that are primarily used for user interface work. The dispatcher is an object (usually a mixin to other objects) that can _register_ callback functions for particular events. Then when a _dispatch_ method is called with an event, the dispatcher calls each callback function in order of their registration and passes them a copy of the event.  In this snippet, I'm presenting a version in Go that has been incredibly stable and useful in my code.

There are three types in the snippet below:

- `EventType` is a `uint16` that represents the type of event that occurs, several constants in the code declare event types along with a string method for human readability. Typing constants this way improves performance in the dispatcher environment.
- `Callback` defines the signature of a function that can be registered.
- `Dispatcher` is the core of the code and wraps a `source` &mdash; that is the actual object that is doing the dispatching.
- `Event` is an interface for event types that has a type, source, and value.

For example, consider if you want to watch a directory for new files being created, you could do something like this:

```go

type DirectoryWatcher struct {
    Dispatcher
    path string // path to directory on disk
}

func (w *DirectoryWatcher) Init(path string) {
    w.path = path
    w.Dispatcher.Init(w)
}

// Watch the given directory and dispatch new file events
func (w *DirectoryWatcher) Watch() error {
    for {
        files, _ := ioutil.ReadDir(w.path)
        for _, file := range files {
            if w.Unseen(file) {
                w.Dispatch(NewFile, file)
            }
        }
        time.Sleep(100 * time.Millisecond)
    }
}
```

This initializes the `DirectoryWatcher` dispatcher with the source as the watcher (so you can refer to exactly which directory was being watched). Then as the watcher looks at the directory for new data every 100 milliseconds, if it sees any files that were `Unseen()` then it dispatches the event.

The dispatcher code is as follows:

<script src="https://gist.github.com/bbengfort/0e2493ea678a8b86978b28b921d98c48.js"></script>

So this works very well but there are a copule of key points:

- When dispatching the event, a single error terminates all event handling. It might be better to create a specific error type that terminates event handling (e.g. do not propagate) and then collect all other errors into a slice and return them from the dispatcher.
- The event can technically be modified by callback functions since it's a pointer. It might be better to pass by value to guarantee that all callbacks see the original event.
- Callback handling is in order of registration, which gets to point number one about canceling event propagation. An alternative is to do all the callbacks concurrently using Go routines; which is something I want to investigate further. 
