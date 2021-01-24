---
aliases:
- /snippets/2016/01/19/better-json-encoding.html
categories: snippets
date: '2016-01-19T14:26:27Z'
draft: false
showtoc: false
slug: better-json-encoding
title: Better JSON Encoding
---

The topic of the day is a simple one: JSON serialization. Here is my question, if you have a data structure like this:

```python
import json
import datetime

data = {
    "now": datetime.datetime.now(),
    "range": xrange(42),
}
```

Why can't you do something as simple as: `print json.dumps(data)`? These are simple Python datetypes from the standard library. Granted serializing a datetime might have some complications, but JSON does have a datetime specification. Moreover, a generator is just an iterable, which can be put into memory as a list, which is exactly the kind of thing that JSON _likes_ to serialize. It feels like this should just work. Luckily, there is a solution to the problem as shown in the Gist below:

{{< gist bbengfort 7e843106c0b0b85a96fb >}}

Ok, so basically this encoder replaces the default encoding mechanism by trying first, and if that doesn't work follows the following strategy:

1. Check if the object has a `serialize` method; if so, return the call to that.
2. Check if the encoder has a `encode_type` method, where &ldquo;type&rdquo; is the type of the object, and if so, return a call to that. Note that this encoder already has two special encodings - one for datetime, and the other for a generator.
3. Wave the white flag; encoding isn't possible but it will tell you exactly how to remedy the situation and not just yell at you for trying to encode something impossible.

So how do you use this? Well you can create complex objects like:

```python

class Student(object):

    def __init__(self, name, enrolled):
        self.name = name         # Should be a string
        self.enrolled = enrolled # Should be a datetime

    def serialize(self):
        return {
            "name": self.name,
            "enrolled": self.enrolled,
        }


class Course(object):

    def __init__(self, students):
        self.students = students # Should be a list of students

    def serialize(self):
        for student in self.students:
            yield student
```

And boom, you can now serialize them with the JSON encoder &mdash; `json.dumps(course, cls=Encoder)`! If you have other types that you don't have direct access to, for example, UUID (part of the Python standard library), then simply extend the encoder and add a `encode_UUID` method.

Note that extending the `json.JSONDecoder` is a bit more complicated, but you could do it along the same lines as the encoder methodology.
