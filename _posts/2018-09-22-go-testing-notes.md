---
layout: post
title:  "Go Testing Notes"
date:   2018-09-22 09:58:12 -0400
categories: programmer
---

In this post I'm just going to maintain a list of notes for Go testing that I seem to commonly need to reference. It will also serve as an index for the posts related to testing that I have to commonly look up as well. Here is a quick listing of the table of contents:

- [Basics](#basics)
- [Table Driven Tests](#table-driven-tests)
- [Fixtures](#fixtures)
    - [Golden Files](#golden-files)
- [Frameworks](#frameworks)
    - [No Framework](#no-framework)
    - [Ginkgo & Gomega](#ginkgo--gomega)
- [Helpers](#helpers)
    - [Temporary Directories](#temporary-directories)
- [Sources and References](#sources-and-references)

## Basics

Just a quick reminder of how to write tests, benchmarks, and examples. A test is written as follows:

```go
func TestThing(t *testing.T) {}
```

Benchmarks are written as follows:

```go
func BenchmarkThing(b *testing.B) {
    for i := 0; i < b.N; i++ {
        // Do Thing
    }
}
```

To run benchmarks, ensure you use the bench flag: `go test -bench=.` with the directory that contains the benchmarks specified. Examples are written as follows:

```go
func Examplething() {
    Thing()
    // Output:
    // thing happened
}
```

Test assertions and descriptions are as follows (most commonly used):

- `t.Error`/`t.Errorf`: equivalent to `t.Log` followed by `t.Fail`, which means that the failure message is printed out, but the test continues running.
- `t.Fatal`/`t.Fatalf`: equivalent to `t.Log` followed by `t.FailNow`, which means the failure message is printed but the test is canceled at that point (all deferred calls will be executed after this step).
- `t.Helper`: marks the test is a helper, when printing file and line info, the function will be skipped. Usually used to make common assertions or perform setup or tear down.
- `t.Skip`/`t.Skipif`: marks the test as skipped, though the test will still fail if any `Error` was called before the skip.

Ref: [Package testing](https://golang.org/pkg/testing/)

## Table Driven Tests

Table driven tests use several language features including composite literals and anonymous structs to write related tests in a compact form. The most compact form of the tests looks like this:

```go
var fibTests = []struct{
    n int        //input
    expected int // expected result
}{
    {1, 1}, {2, 1}, {3, 2}, {4, 3}, {5, 5}, {6, 8}, {7, 13},
}
```

Of course it is also possible to define an internal struct in the test package (if using `pkg_test`) for reusable test construction. Hooking it up is as simple as:

```go
func TestFig(t *testing.T) {
    for _, tt := range fibTests {
        actual := Fib(tt.n)
        if actual != expected {
            t.Errorf("Fig(%d): expected %d, actual %d", tt.n, tt.expected, actual)
        }
    }
}
```

Ref: [Dave Cheney &mdash; Writing table driven tests in Go](https://dave.cheney.net/2013/06/09/writing-table-driven-tests-in-go)

## Fixtures

When using the Go testing package, the test binary will be executed with its working directory set to the source directory of the package being tested. Additionally, the Go tool will ignore directories that start with a period, an underscore, or matches the word `testdata`. This means that you can create a directory called `testdata` and store fixtures there. You can then load data as follows:

```go
func loadFixture(t  *testing.T, name string) []byte {
    path := filepath.Join("testdata", name)
    bytes, err := ioutil.Readfile(path)
    if err != nil {
        t.Fatalf("could not open test fixture %s: %s", name, err)
    }
    return bytes
}
```

Ref: [Dave Cheney &mdash; Test fixtures in Go](https://dave.cheney.net/2016/05/10/test-fixtures-in-go)

### Golden Files

When testing complicated or large output, you can save the data as an output file named `.golden` and provide a flag for updating it:

```go
var update = flag.Bool("update", false, "update .golden files")

func TestSomething(t *testing.T) {
    actual := doSomething()

    golden := filepath.Join("testdata", tc.Name+".golden")
    if *update {
        ioutil.WriteFile(golden, actual, 0644)
    }

    expected, _ := ioutil.ReadFile(golden)
    if !bytes.Equal(actual, expected) {
        // Fail!
    }
}
```

Ref: [Povilas Versockas &mdash; Go advanced testing tips & tricks](https://medium.com/@povilasve/go-advanced-tips-tricks-a872503ac859)

## Frameworks

### No Framework

Ben Johnson makes a good argument for not using a testing framework. Go has a simple yet powerful testing framework. Frameworks are a barrier to entry for contributors to code. Frameworks require more dependencies to be fetched and managed. To reduce the verbosity, you can include simple test assertions as follows:

```go
func assert(tb testing.TB, condition bool, msg string)
func ok(tb testing.TB, err error)
func equals(tb testing.TB, exp, act interface{})
```

This way you can write tests as:

```go
func TestSomething(t *testing.T) {
    value, err := DoSomething()
    ok(t, err)
    equals(t, 100, value)
}
```

I certainly like the simplicity of this idea and on many of my small packages I simply write tests like this. However, in larger projects, it feels like test organization can quickly get out of control and I don't know what I've tested and where.

Ref: [Ben Johnson &mdash; Structuring Tests in Go](https://medium.com/@benbjohnson/structuring-tests-in-go-46ddee7a25c)
Ref: [Testing Functions for Go](https://github.com/benbjohnson/testing)

### Ginkgo & Gomega

Many of my projects have started off using [Ginkgo](http://onsi.github.io/ginkgo/) and [Gomega](http://onsi.github.io/gomega/) for testing. Ginkgo provides BDD style testing to write expressive and well organized tests. Gomega provides a matching library for performing test-related assertions.

To bootstrap a test suite (after installing the libraries with `go get`) you would run `ginkgo bootstrap`. This creates the test suite which runs the tests. You can then generate tests by running `ginkgo generate thing` to create `thing_test.go` with the test stub already inside it:

```go
package thing_test

import (
    . "/path/to/thing"
    . "github.com/onsi/ginkgo"
    . "github.com/onsi/gomega"
)

var _ = Describe("Thing", func() {

    var thing Thing

    BeforeEach(func() {
        thing = new(Thing)
    })

    It("should do something", func() {
        Ω(thing.Something()).Should(Succeed())
    })

})
```

While I do like the use of this test framework, it's primarily for the organization of the tests and the runner.

## Helpers

Helper functions can be marked with `t.Helper()`, which excludes their line and signature information from the test error traceback. They can be used to do setup for the test case, unrelated error checks, and can even clean up after themselves!

### Temporary Directories

Often, I need a temporary directory to store a database in or write files to. I can create the temporary directory with this helper function, which also returns a function to cleanup the temporary directories.

```go
const tmpDirPrefix = "mytests"

func tempDir(t *testing.T, name string) (path string, cleanup func()) {
    t.Helper()

    tmpDir, err = ioutil.TempDir("", tmpDirPrefix)
    if err != nil {
        t.Fatalf("could not create temporary directory: %s", err)
    }

    return filepath.Join(tmpDir, name), func() {
        err = os.RemoveAll(tmpDir)
        if err != nil {
            t.Errorf("could not remove temporary directory: %s", err)
        }
    }
}
```

This can be used with the cleanup function pretty simply:

```go
func TestThing(t *testing.T) {
    dir, cleanup := tempDir(t, "db")
    defer cleanup()

    ...
}
```

Another version that I have in some of my tests creates a temporary directory for all of the tests, stored in a variable at the top level, any caller asking for a directory can create it, but it won't be overridden if if already exists; then any test that cleans up will clean up that directory.

## Sources and References

- [Package testing](https://golang.org/pkg/testing/)
- [Dave Cheney &mdash; Writing table driven tests in Go](https://dave.cheney.net/2013/06/09/writing-table-driven-tests-in-go)
- [Dave Cheney &mdash; Test fixtures in Go](https://dave.cheney.net/2016/05/10/test-fixtures-in-go)
- [Ben Johnson &mdash; Structuring Tests in Go](https://medium.com/@benbjohnson/structuring-tests-in-go-46ddee7a25c)
- [Povilas Versockas &mdash; Go advanced testing tips & tricks](https://medium.com/@povilasve/go-advanced-tips-tricks-a872503ac859)

Not related to testing, but saved for reference for a later godoc notes post:

- [Elliot Chance &mdash; Godoc: Tips & Tricks](http://elliot.land/post/godoc-tips-tricks)
- [Andrew Gerrand &mdash; Godoc: documenting Go code](https://blog.golang.org/godoc-documenting-go-code)
