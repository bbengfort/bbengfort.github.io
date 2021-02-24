---
title: "Go Closures & Interfaces"
date: 2021-02-23T08:28:22-05:00
draft: false
categories: observations
showtoc: true
---

Strict typing in the Go programming language provides safety and performance that is valuable even if it does increase the verbosity of code. If there is a drawback to be found with strict typing, it is usually felt by library developers who require flexibility to cover different use cases, and most often appears as a suite of type-named functions such as `lib.HandleString`, `lib.HandleUint64`, `lib.HandleBool` and so on. Go does provide two important language tools that do provide a lot of flexibility in library development: _closures_ and _interfaces_, which we will explore in this post.

## Closures

Closures may be one of the most misunderstood concepts in computer science because the term is rooted in language-specific constructs such as scope, stack vs heap allocation, and anonymous functions. Perhaps the most precise definition of a closure is:

> The combination of a _function_ with an _environment_ where the environment is a mapping of all free variables available to the function to the value or reference of those variables at the time the closure was created.

Said a bit more simply, closures can be thought of as a packaging of specific state with a specific function in an isolated (closed) bundle. If this sounds similar to object-oriented programming, then you'd be right - in fact, programming languages that allow closures typically implement them with a special data structure analogous to an object or by implementing function objects. This has implications for stack vs heap allocation and defines what kinds of programming languages could support closures (not all can). Note that languages that natively support closures also tend to use garbage collection.

So why would you use a closure instead of an object? One very common answer is simplicity - compare the following code that implements a closure with code that implements a struct with a method:

```go
package main

import "fmt"

func Counter() func () int {
    var i int
    return func() int {
        i++
        return i
    }
}

func main() {
    counter := Counter()
    fmt.Println(counter())
    fmt.Println(counter())

    other := Counter()
    fmt.Println(other())
    fmt.Println(counter())

}
```

In the closure code, the `Counter` function returns the closure, the `func() int`, whose environment is the variable `i`. When the closure is called, it increments its state variable `i` and maintains that state across multiple calls. If a new closure, `other`, is created its state is separate from the state of the original counter.

```go
package main

import "fmt"

type Counter struct {
    i int
}

func (c *Counter) Incr() int {
    c.i++
    return c.i
}

func main() {
    counter := new(Counter)
    fmt.Println(counter.Incr())
    fmt.Println(counter.Incr())

    other := new(Counter)
    fmt.Println(other.Incr())
    fmt.Println(counter.Incr())

}
```

The struct code defines a `Counter` struct with an internal int `i` as its state, then provides a method `Incr` to modify and return that state in a similar way to the closure code.

The simplicity argument is that the counter only uses a single definition instead of two (e.g. a definition for the closure function instead of one each for the struct and method definitions) and reduces the lexical complexity - e.g. removing the need for creating and initializing a new struct and the dotted method call. However, they are the same number of lines of code and in my opinion the `struct` code is more flexible. More importantly, the struct code is more performant:

```
BenchmarkCounterStruct-8    	1000000000	         0.278 ns/op
BenchmarkCounterClosure-8   	27671817	        39.6   ns/op
```

These benchmarks test the allocation/creation of either the struct or the closure and one call to increment. The closure is 142x slower likely because of the overhead of creating the additional closure structure and the allocations required to add the environment and mapping to the stack.

A better argument for the use of closures is to allow flexibility in code.

Unlike a struct, the state of a closure need not be defined prior to its use since its state is _all variables in the enclosing scope_. This is why _anonymous_ or _lambda_ functions are inextricably tied with closures, since in Go an anonymous function is required to create a closure. Anonymous functions are not necessarily closures, however, they're simply functions that are not bound to a name. Still, it's tough to come up with a use case in Go where an anonymous function is not a closure.

Capturing variables in the enclosing scope in the environment of the closure brings us to the primary use case for closures in Golang: kicking off go routines to do work. Consider the following example that creates and calls 11 closures as go routines:

```go
package main

import (
    "fmt"
    "log"
)

func main() {
    // Create the done and errc channels in the scope of the main function. These
    // channels are the primary local variables that we're going to enclose in the
    // environment of all 11 closures created in this function.
    errc := make(chan error, 1)
    done := make(chan int, 1)

    // Instantiate 10 worker closures that uses the errc and done channels.
    for i := 0; i < 10; i++ {
        // Note that this closure takes as input an integer j, and the for loop
        // variable, i, is passed to this function as an argument rather than the
        // closure accessing the enclosed i. More on this later.
        go func(j int) {
            if err := doWork(); err != nil {
                errc <- err
            }
            done <- j
        }(i)
    }

    // The 11th closure reads off of the done channel and marks progress, closing
    // the error channel when all work is complete to signal to the main routine
    // that the work is finished.
    go func() {
        for i := 0; i < 10; i++ {
            j := <-done
            fmt.Printf("worker %d done in %d position\n", j, i+1)
        }

        // When done, close the error channel
        close(errc)
    }()

    // The main routine continues, blocking on the error channel to allow the
    // workers to do their thing rather than simply exiting. If it receives an
    // error, the program is terminated early.
    for err := range errc {
        if err != nil {
            log.Fatal(err)
        }
    }

    // When the error channel is closed by the 11th closure, we get to this point
    // and exit the program with a success message!
    fmt.Println("done successfully!")
}
```

In this snippet of code the calls to `go func() {}()` are the simultaneous definition of an anonymous function, the creation of a closure, and the execution of a go routine. In this context, the anonymous function is what is allowing the closure to be created. Consider the valid execution of a named function with a similar function body, `go doWork(i)`, to kick off the go routine; in this case the compiler would error with `undefined: errc` or `undefined: done` since the named function is not a closure and the two channels would have to be passed explicitly to the function.

This also brings us to the major gotcha with closures - the state that they enclose is a _shared_ state that is readable and writable by all routines. Note that all routines in the snippet above could easily send on or read from any of the channels in the enclosing state. This is precisely why it is so important to use channels or lower level atomics/mutexes for synchronization across go routines. One key place that is a common error for Go programmers is the `for` loop that creates the 10 workers. Although the closure has access to the variable `i`, as the loop changes, so does the variable. Therefore if it were to `done <- i` rather than `j`, then it's likely only `9` would be printed to the console. By creating an argument `j` and passing `i` into the function, the variable is escaped out of the outer scope and placed into the inner scope of the closure function.

And finally, a last comment on closures in Go - they can be typed. One common pattern is to create a factory function that has an outer scope to do some work and returns a closure to do the handling. For example, the go routines from above could be refactored as follows:

```go
// Specify the type of the worker function, that is a function that takes an int
type worker func(i int)

// Worker factory creates a new worker function enclosing the outer scope that
// contains the done and errc channels. Note that the directionality is now
// specified, the worker can only send on the channel, not recv.
func workerFactory(done chan<- int, errc chan<- error) (worker, err) {
    // Check to make sure the worker can be created, otherwise return error

    // Create the closure and return it
    return func(i int) {
        if err := doWork(); err != nil {
            errc <- err
        }
        done <- i
    }, nil
}

func main() {
    errc := make(chan error, 1)
    done := make(chan int, 1)

    // Instantiate 10 workers to do the work, first checking to ensure the worker
    // can be created by the factory.
    for i := 0; i < 10; i++ {
        worker, err := workerFactory(done, errc)
        if err != nil {
            log.Fatal(err)
        }
        go worker(i)
    }

    ...
}
```

Although it appears that there is no closure created here, in fact there is. Instead of the enclosing the scope of the `main` function, it is the scope of `workerFactory` that is enclosed in the closure. This also gives us the opportunity to specify the directionality of the channels so that the worker can only send and not recv on the `done` and `errc` channels. This pattern is useful when some work needs to be done to set up the worker(s) (e.g. connect to a database) or check to make sure other constraints are satisfied (e.g. "only launch 100 workers").

Closures and function types are one of the two primary ways Go provides flexibility for library code, the other is interfaces.

## Interfaces

Interfaces are types in programming that specify the _behavior_ of an entity.

I've chosen this definition carefully because interfaces are commonly used in object-oriented programming languages such as Java and may have flexible interpretations for duck-typed languages, e.g. "if it looks like a duck, it quacks like a duck, it walks like a duck - then it's a duck". In a strictly typed language like Go, an interface must be a type. More specifically in Go, an interface is "a named collection of method signatures".

The most common interface that we use in go is the `error` interface, which is defined as follows:

```go
type error interface {
    Error() string
}
```

When we declare a function that returns an error, we are actually specifying that the function returns a struct that _implements_ the `error` interface, e.g. it has an `Error` method that returns a string. The two most common ways we create errors in Go are via `fmt.Errorf` and `errors.New` - both of these functions actually return a `*errors.errorString` type (use `fmt.Printf("%T\n", err)` to print the type of an object or an error). We could just as easily do the following (which is also very common):

```go
type Error struct {
    code uint32
    msg string
}

func (e *Error) Error() string {
    return fmt.Errorf("[%d] %s", e.code, e.msg)
}


func myfunc() error {
    return &Error{code: 32, msg: "it didn't work"}
}
```

Interfaces therefore give us the opportunity to pass around different base types to different functions even in a strictly typed environment, because the function will know what method it can call using that type. One of the best examples in the Go standard library of the flexibility of types is the `io` library and the `io.Reader` and `io.Writer` interfaces:

```go
type Reader interface {
        Read(p []byte) (n int, err error)
}

type Writer interface {
        Write(p []byte) (n int, err error)
}
```

These interfaces mean that you can create a function that accepts an either an `*os.File` or a `*bytes.Buffer` or some other socket connection, etc. and read or write to it using the same interface. You can also compile interfaces into a single interface, e.g.

```go
type ReadWriter interface {
    io.Reader
    io.Writer
    io.Closer
}
```

This interface requires objects to have all of the `Read([]byte) (int, error)`, `Write([]byte) (int, error)`, and `Close() error` methods. In fact, the `io.ReadCloser` interface is such a compiled interface in the standard library. The best practice for flexbility with interfaces is to define the minimum number of methods required for a single interface, and to build them up into larger interfaces as needed (without letting it get out of hand). For example:

```go
type Worker interface {
    Handle(Task) error
    Name() string
}

type Preparer interface {
    Before() error
}

type Janitor interface {
    Cleanup() error
}

type Workflow interface {
    Preparer
    Worker
    Janitor
}
```

Library code might have a single method that does all of the workflow using a `Worfklow` object, but can be made more flexbile by calling individual functions for the other interfaces. By requiring only the interface that is needed for the input of the function, the testing becomes easier and the library more robust.

Let's get into some common gotchas. Consider the following interface:

```go
type Handler interface {
    Handle() error
}
```

First, arguments to functions that accept `Handler` types are defined as follows:

```go
func Do(h Handler) error {
    return h.Handle()
}
```

This can be confusing because you might be passing a pointer to a struct that implements `Handler`, but if you create the following definition:

```go
func Do(h *Handler) error {}
```

You'll receive the following error:

```text
cannot use valueHandler literal (type valueHandler) as type *Handler in argument to Do:
	*Handler is pointer to interface, not interface
```

That's because `Handler` is an interface, and the struct that implements `Handler` could be either a value or a pointer. Whether it is a value or pointer depends on how the method is implemented:

```go
type pointerHandler struct {}

func (*pointerHandler) Handle() error {
    return nil
}

type valueHandler struct {}

func (valueHandler) Handle() error {
    return nil
}
```

Given these methods the following are valid:

```go
Do(&pointerHandler{})
Do(valueHandler)
```

But the following is not valid:

```go
Do(pointerHandler{})
```

Which will cause the following error to be raised:

```text
cannot use pointerHandler literal (type pointerHandler) as type Handler in argument to Do:
	pointerHandler does not implement Handler (Handle method has pointer receiver)
```

Somewhat confusingly, `Do(&valueHandler{})` is allowed, but when `h.Handle` is called it will be called with a copy of the value passed in which means that the handler will not be able to change the data on the original referenced struct. I tend to try to avoid this situation because of the confusion it might cause.

This leads us finally to `interface{}` and `nil`. The empty interface, `interface{}` is an interface type that specifies no methods. Because it specifies no methods, it may hold values of any type since every type implements at least no methods. Practically speaking `interface{}` is used as a catchall as a preliminary to custom type checking, for example:

```go
func serialize(v interface{}) string {
    switch t := v.(type) {
    case int:
        return fmt.Sprintf("%X", v)
    case bool:
        if t {
            return "true"
        } else {
            return "false"
        }
    case string:
        return t
    case error:
        return t.Error()
    default:
        return fmt.Sprintf("unknown type %T", v)
    }
}
```

Here, a _type switch_ is used to test the type of the value `v`, the `case` statements must use types to test and the assigned value `t` is a variable of the type matched with the value of `v`. Using type assertions also allows unpack the base type of an interface. Using our `Error` example from earlier:

```go
if e, ok := err.(*Error); ok {
    // e is an *Error from our code, so we can access it as needed.
    if e.code == 32 {
        ...
    }
}
```

This kind of type assertion is only able to be performed on an interface type; otherwise the type assertion would be irrelevant.

The final question we should ask ourselves is why we can use `nil` as a value for an interface, e.g. `return nil` instead of an error. All types in Go have a "zero value" since there is no `None` or `null` in Go. The zero value for an int is `0`, for a bool is `false`, for a string is `""`. If you define a struct value without a pointer, e.g. when you do `time.Now()` you get back a `time.Time` not a `*time.Time`, then the zero value is an empty struct, e.g. `time.Time{}`, whose internal values are all zero values for their types. The zero value for maps, slices, channels, and pointers is `nil`.

Consider the following code:

```go
var (
    i int
    s string
    t time.Time
    m map[string]string
)
```

These variables are declared but not assigned to, therefore they will all be allocated with their zero value, `0`, `""`, `time.Time{}`, and `nil` respectively. Because `nil` is the zero value for all pointers, and because pointers can be used with interface types, passing `nil` in for an interface is effectively the same as saying "pass the zero value of the interface". E.g. `return nil` is pass the zero value of an `error`. This also means that the nil type check can work directly with interfaces:

```go
type Handler interface {
    Handle() error
}


func Do(h Handler) error {
    if h == nil {
        return errors.New("nil handler")
    }
    return h.Handle()
}
```

Be careful with this type of check, however, as non-nil zero value types can also be used for an interface:

```go
type IntHandler int

func (IntHandler) Handle() error {
    return nil
}

func main() {
    fmt.Println(Do(nil))
    fmt.Println(Do(IntHandler(0)))
}
```

In this case, only the `Do(nil)` is correctly handled, whereas the zero-valued `IntHandler` is not `nil` and therefore its handle method is called.

## net/http Example

Closures and Interfaces might not seem like a natural pairing for discussion, however they are both essential to effective and flexible library development. One of the best examples of this is in Go's standard library `net/http` package which allows Go developers to quickly and easily spin up an http server.

The [documentation](https://golang.org/pkg/net/http/) describes how to get a simple server going with the `DefaultServeMux` using `http.Handle` and `http.HandleFunc`. A "mux" (short for "multiplexer") passes incoming requests to the correct handler based on information from the request. By default, the path of the URL is used to determine which handler to use. In the following example the mux ensures that requests to `http://localhost:8080/foo` are handled by the `fooHandler` and to `http://localhost:8080/bar` are handled by the function passed to `http.HandleFunc`. Here is the example from the documentation:

```go
http.Handle("/foo", fooHandler)

http.HandleFunc("/bar", func(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, %q", html.EscapeString(r.URL.Path))
})

log.Fatal(http.ListenAndServe(":8080", nil))
```

This example shows both the interface and closure use cases for setting up an http server. In the first line of code, the `http.Handle` function takes a struct that implements the `http.Handler` interface as its second argument. In the second, the `http.HandleFunc` takes as its second argument a function of type `http.HandlerFunc`, which is a perfect use case for a closure. Finally the `http.ListenAndServe` method is called to serve requests on the localhost on port :8080; if it returns an error, it will be passed to `log.Fatal`. Let's break this down:

The `http.Handler` interface is defined as follows:

```go
type Handler interface {
    ServeHTTP(http.ResponseWriter, *http.Request)
}
```

Therefore, to implement the `fooHandler` we might do something as follows:

```go
type FooContext struct {
	ID   int
	Name string
}

type Foo struct {
	content *template.Template
}

func (f *Foo) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	context := FooContext{ID: 1, Name: "Lydia"}
	f.content.Execute(w, context)
}

func main() {
	// Create a new Foo handler with the specified template loaded from disk.
	fooHandler := &Foo{
		content: template.New("foo.html"),
	}
	fooHandler.content = template.Must(fooHandler.content.ParseFiles("foo.html"))

	http.Handle("/foo", fooHandler)
}
```

Here, the `Foo` struct implements `Handler` with its `ServeHTTP` method. In this case, it maintains state with an HTML template that is loaded from a file and that template is executed with a context and written into the response body. You could see how the `ServeHTTP` method might use the request to look up information in a database to use for the context or do other processing on behalf of the user.

The `http.HandlerFunc` type is defined as follows:

```go
type HanderFunc func(http.ResponseWriter, *http.Request)
```

The function signature is identical to the method signature in the interface. In both cases the library expects the user to handle the incoming request and write the response into the response writer. Using `http.HandleFunc` provides the opportunity to create a closure to maintain simple state. One very common use case for this is to create a chain of middleware functions that wrap other handlers. Consider the following middleware stub code:

```go
func middleware(next http.HandlerFunc) http.HandlerFunc {
    // One-time setup/initialization of the middleware coded here.
    ...

    // Create the closure to return as the handler function
    return func(w http.ResponseWriter, r *http.Request) {
        // Before the next request is handled, e.g. handle the incoming request
        // If this function returns before the next handler is called, then it short
        // circuits the request and no downstream handlers will be called.
        ...

        // Execute the next handler in the change
        next(w, r)

        // After the request has been handled, e.g. handle the outgoing response
        ...
    }
}
```

This allows you to create a flow of control such that the outer middleware are handled first until some final middleware, then the response goes back out through the layers until the response is returned to the user. Common middleware steps for an http server include tracing, logging, authentication, content negotation, and more! This might look something as follows:

```go
func logging(next http.Handler) http.Handler {
    log := logger.New()
    return func(w http.ResponseWriter, r *http.Request) {
        next(w, r)
        log.Info("request handled")
    }
}

func authentication(username, password string, next http.Handler) http.Handler {
    token := fmt.Sprintf("%s:%s", username, password)
    return func(w http.ResponseWriter, r *http.Request) {
        header := r.Header.Get("Authorization")
        if header != token {
            http.Error(w, "username/password not recognized", http.StatusForbidden)
            return
        }

        next(w, r)
    }
}

func final(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("Hello World!"))
}


func main() {
    // Create middleware
    handler := logging(authenticate(username, password, final))
}
```

The closures allow us to easily construct handler-specific chains of http request handling that are intuitive and easily adaptible!

## Wrap-Up

Strict typing helps programmers write safe and highly-performant code and language constructs like interfaces and closures help them write flexible code even with strict typing. Careful consideration of how to define interfaces and libraries that use closures can make working with Go libraries more productive and enjoyable!