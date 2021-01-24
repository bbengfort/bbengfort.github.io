---
categories: snippets
date: "2017-08-18T15:33:35Z"
title: Rapid FS Walks with ErrGroup
---

I've been looking for a way to quickly scan a file system and gather information about the files in directories contained within. I had been doing this with multiprocessing in Python, but figured Go could speed up my performance by a lot. What I discovered when I went down this path was the [`sync.ErrGroup`](https://godoc.org/golang.org/x/sync/errgroup), an extension of the `sync.WaitGroup` that helps manage the complexity of multiple go routines but also includes error handling!

The end result of this exploration was a utility called [urfs](https://github.com/bbengfort/urfs) &mdash; which you can install on your system to take a uniform random sample of files in a directory or to compute the number of files and bytes per directory. This utility is also extensible to a large number of functionality that requires rapid walking of a file system like search or other utilities.

This post is therefore a bit of a walkthrough on using `sync.ErrGroup` for scanning a file system and applying arbitrary functions. First a couple of types:

```go
type WalkFunc func(path string) (string, error)

type FSWalker struct {
	Workers    int             
	SkipHidden bool            
	SkipDirs   bool            
	Match      string          
	root       string          
	paths      chan string     
	nPaths     uint64          
	results    chan string     
	nResults   uint64        
	group      *errgroup.Group
	ctx        context.Context
	started    time.Time       
	duration   time.Duration   
}
```

The first type is a generic function that can be passed to the `Walk` method of the `FSWalker`. The `FSWalker` maintains state with a variety of channels, and of course the `errgroup.Group` object. The SkipHidden, SkipDirs, and Match properties allow us to filter path types being passed to Walk.

To initialize `FSWalker`:

```go
func (fs *FSWalker) Init(ctx context.Context) {
	// Set up FSWalker defaults
	fs.Workers = DefaultWorkers
	fs.SkipHidden = true
	fs.SkipDirs = true
	fs.Match = "*"

    // Create the context for the errgroup
	if ctx == nil {
		// Create a new context
		ctx = context.Background()
		deadline, ok := fs.ctx.Deadline()
		if ok {
			ctx, _ = context.WithDeadline(ctx, deadline)
		}
	}

    // Create the err group
    fs.group, fs.ctx = errgroup.WithContext(ctx)

    // Create channels and instantiate other statistics variables
	fs.paths = make(chan string, DefaultBuffer)
	fs.results = make(chan string, DefaultBuffer)
	fs.nPaths = 0
	fs.nResults = 0
	fs.started = time.Time{}
	fs.duration = time.Duration(0)
}
```

Ok, so we're doing a lot of work here, but things get paid off in the Walk function where we keep track of the number of paths we've seen at a root directory, passing them off to a `WalkFunc` using a variety of Go routines:

```go
func (fs *FSWalker) Walk(path string, walkFn WalkFunc) error {
	// Compute the duration of the walk
	fs.started = time.Now()
	defer func() { fs.duration = time.Since(fs.started) }()

	// Set the root path for the walk
	fs.root = path

	// Launch the goroutine that populates the paths
	fs.group.Go(func() error {
        // Ensure that the channel is closed when all paths loaded
    	defer close(fs.paths)

        // Apply the path filter to the filepath.Walk function
    	return filepath.Walk(fs.root, fs.filterPaths)
    })

	// Create the worker function and allocate pool
	worker := fs.worker(walkFn)
	for w := 0; w < fs.Workers; w++ {
		fs.group.Go(worker)
	}

	// Wait for the workers to complete, then close the results channel
	go func() {
		fs.group.Wait()
		close(fs.results)
	}()

	// Start gathering the results
	for _ = range fs.results {
		fs.nResults++
	}

	return fs.group.Wait()
}
```

So this is a lot of code, let's step through it. The first thing we do is set the started time to now, and defer a function to compute the duration as the difference between the time at the end of the function and the start function. We also set the root value. We then launch a go routine in the `ErrGroup` by using `fs.group.Go(func)` &mdash; this function must have the signature `func() error`, so we use an anonymous function to kick off the `filepath.Walk`, which starts walking the directory structure, adding paths that match the filter criteria to a buffered channel called `fs.paths`, more on this later. This channel must be closed on complete so that our worker go routines complete, more on that later.

Next we create a worker function using our worker method and walk function. The workers read paths off the `fs.paths` channel, and apply the walkFn to each path individually. Note that we use a pool-like structure here, limiting the number of workers to 5000 &mdash; this is so we don't get a "too many files open" error when we exhaust the number of file descriptors since Go has unlimited go routines. The worker definitions is here:

```go
func (fs *FSWalker) worker(walkFn WalkFunc) func() error {
	return func() error {
		// Apply the function all paths in the channel
		for path := range fs.paths {
			// avoid race condition
			p := path

			// apply the walk function to the path and return errors
			r, err := walkFn(p)
			if err != nil {
				return err
			}

			// store the result and check the context
			if r != "" {

				select {
				case fs.results <- r:
				case <-fs.ctx.Done():
					return fs.ctx.Err()
				}
			}

		}
		return nil
	}
}
```

As you can see, the worker function just creates a closure with the signature of our `ErrGroup` function, so that we can pass it to the wait group. All the worker function does is range over the paths channel, applying the path to the `walkFn`.

Finally, we kick off another go routine that waits until all the workers have stopped, and when it does, we close our results channel. We do this so that we can start gathering results, immediately; we don't have to wait. We can do this by simply ranging over the results channel and adding the number of results. A final wait at the end means that we can wait for all go routines to complete.

Lastly the filter function. We want to ignore files and directories that are hidden, e.g. start with a "." or a "~" on Unix systems. We also want to be able to pass a glob like matcher, e.g. `"*.txt"` to only match text files. The filter function is here:

```go
// Internal filter paths function that is passed to filepath.Walk
func (fs *FSWalker) filterPaths(path string, info os.FileInfo, err error) error {
	// Propagate any errors
	if err != nil {
		return err
	}

	// Check to ensure that no mode bits are set
	if !info.Mode().IsRegular() {
		return nil
	}

	// Get the name of the file without the complete path
	name := info.Name()

	// Skip hidden files or directories if required.
	if fs.SkipHidden {
		if strings.HasPrefix(name, ".") || strings.HasPrefix(name, "~") {
			return nil
		}
	}

	// Skip directories if required
	if fs.SkipDirs {
		if info.IsDir() {
			return nil
		}
	}

	// Check to see if the pattern matches the file
	match, err := filepath.Match(fs.Match, name)
	if err != nil {
		return err
	} else if !match {
		return nil
	}

	// Increment the total number of paths we've seen.
	atomic.AddUint64(&fs.nPaths, 1)

	select {
	case fs.paths <- path:
	case <-fs.ctx.Done():
		return fs.ctx.Err()
	}

	return nil
}
```

And that's it, with this simple framework, you can apply an arbitrary `walkFn` to all paths in a directory, matching a specific criteria. The big win here is to manage all of the go routines using the `ErrGroup` and a `context.Context` object.

The following post: [Run strikingly fast parallel file searches in Go with sync.ErrGroup](https://www.oreilly.com/learning/run-strikingly-fast-parallel-file-searches-in-go-with-sync-errgroup) by [Brian Ketelsen](https://www.oreilly.com/people/7e856-brian-ketelsen) was the primary inspiration for the use of sync.ErrGroup.
