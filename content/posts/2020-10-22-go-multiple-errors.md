---
categories: snippets
date: "2020-10-22T11:45:41Z"
title: Managing Multi-Errors in Go
---

This post is a response to [Go: Multiple Errors Management](https://medium.com/a-journey-with-go/go-multiple-errors-management-a67477628cf1). I've dealt with a multiple error contexts in a few places in my Go code but never created a subpackage for it in `github.com/bbengfort/x` and so I thought this post was a good motivation to explore it in slightly more detail. I'd also like to make error contexts for routine cancellation a part of my standard programming practice, so this post also investigates multiple error handling in a single routine or multiple routines like the original post.

Multi-error management for me usually comes in the form of a `Shutdown` or `Close` method where I'm cleaning up a lot of things and would like to do everything before I handle errors:

```go
func (s *Server) Shutdown() (err error) {
    errs = make([]error, 0, 4)

    if err = s.router.GracefulStop(); err != nil {
        errs = append(errs, err)
    }

    if err = s.db.Close(); err != nil {
        errs = append(errs, err)
    }

    if err = s.meta.Flush(); err != nil {
        errs = append(errs, err)
    }

    if err = s.meta.Close(); err != nil {
        errs = append(Errs, err)
    }

    // Best case scenario first
    if len(errs) == 0 {
        return nil
    }

    if len(errs) == 1 {
        return errs[0]
    }
    return fmt.Errorf("%d errors occurred during shutdown", len(errs))
}
```

Obviously this is less than ideal in a lot of ways and using [`go-multierror`](https://github.com/hashicorp/go-multierror) by HashiCorp or [`multierr`](https://github.com/uber-go/multierr) by Uber cleans things up nicely. Better yet, we could implement a simple type to handle reporting and appending:

```go
// MultiError implements the Error interface so it can be used as an error while also
// wrapping multiple errors and easily appending them during execution.
type MultiError struct {
    errors []error
}

// Error prints a semicolon separated list of the errors that occurred. The Report
// method returns an error with a newline separated bulleted list if that's better.
func (m *MultiError) Error() string {
    report := make([]string, 0, len(m)+1)
    report = append(report, fmt.Sprintf("%d errors occurred", len(m)))
    for _, err := range m {
        report = append(report, err.Error())
    }
    return strings.Join(report, "; ")
}

// Appends more errors onto a MultiError, ignoring nil errors for ease of use. If the
// MultiError hasn't been initialized, it is in this function. If any of the errs are
// MultiErrors themselves, they are flattened into the top-level multi error.
func (m *MultiError) Append(errs ...error) {
    if m.errors == nil {
        m.errors = make([]error, 0, len(errs))
    }

    for _, err := range errs {
        // ignore nil errors for quick appends.
        if err == nil {
            continue
        }

        switch err.(type) {
        // flatten multi-error to the top level.
        case *MultiError:
            if len(err.errors) > 0 {
                m.errors = append(m.errors, err.errors...)
            }
        default:
            m.errors = append(m.errors, err)
        }
    }
}

// Get returns nil if no errors have been added, the unique error if only one error
// has been added, or the multi-error if multiple errors have been added.
func (m MultiError) Get() error {
    switch len(m) {
    case 0:
        return nil
    case 1:
        return m[0]
    default:
        return m
    }
}
```

This code simplifies the process a bit and adds more helper functionality, but I haven't benchmarked it yet. New usage would be as follows:

```go
func (s *Server) Shutdown() (err error) {
    var merr MultiError

    merr.Append(s.router.GracefulStop())
    merr.Append(s.db.Close())
    merr.Append(s.meta.Flush())
    merr.Append(s.meta.Close())

    return merr.Get()
}
```

In real code, though, I think I might prefer to use `go-multierror` as it has a lot more functionality and a slightly more intuitive implementation. This code was mostly for commentary purposes.

The real thing I need to remember is goroutine cancellation contexts using `errgroup`:

```go
func action(ctx context.Context) (err error) {
	// Note that the action must listen for the cancellation!
	timer := time.NewTimer(time.Duration(rand.Int63n(4000)) * time.Millisecond)
	select {
	case <-timer.C:
		if rand.Float64() < 0.2 {
			return errors.New("something bad happened")
		}
	case <-ctx.Done():
		return nil
	}
	return nil
}

func main() {
	g, ctx := errgroup.WithContext(context.Background())
	for i := 0; i < 3; i++ {
		g.Go(func() (err error) {
			for j := 0; j < 3; j++ {
				if err = action(ctx); err != nil {
					return err
				}
			}
			return nil
		})
	}
	if err := g.Wait(); err != nil {
		log.Fatal(err)
	}
}
```

The thing the blog post forgot to mention is that the go routine must be able to actively cancel its operation by listening on the `ctx.Done()` channel in addition to a channel that signals the operation is done (in the above example, the timer channel that is just causing the routine to sleep). If the `action` function does not listen to the `ctx.Done()` channel, even though the _error propagates_ to the `g.Wait()` and returns, and `cancel()` for the context is called; the program will not terminate "early" because no action is waiting for the cancellation signal.