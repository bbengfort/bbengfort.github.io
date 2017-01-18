---
layout: post
title:  "Generic JSON Serialization with Go"
date:   2017-01-18 11:31:06 -0500
categories: snippets
---

This post is just a reminder as I work through handling JSON data with Go. Go provides first class JSON support through its standard library `json` package. The interface is simple, primarily through `json.Marshal` and `json.Unmarshal` functions which are analagous to typed versions of `json.load` and `json.dump`. Type safety is the trick, however, and generally speaking you define a `struct` to serialize and deserialize as follows:

```go
type Person struct {
    Name   string `json:"name,omitempty"`
    Age    int    `json:"age,omitempty"` 
    Salary int    `json:"-"` 
}

op := &Person{"John Doe", 42} 
data, _ := json.Marshal(op) 

var np Person 
json.Unmarshall(data, &np) 
```

So this is all well and good, until you start wanting to just send around arbirtray data. Luckly the `json` package will allow you to do that using reflection to load data into a `map[string]interface{}`, e.g. a dictionary whose keys are strings and whose values are any arbitrary type (anything that implements the null interface, that is has zero or more methods, which all Go types do). So you might see code like this:  

<script src="https://gist.github.com/bbengfort/a06c87f6cdea029eda5e432be0242978.js"></script>

Did you catch the surprise? That's right, the age `int` got deserialized as a `float64`! Anyway, this whole post is about how long it took me to figure out that brand of reflection and how to avoid errors in the future. 
