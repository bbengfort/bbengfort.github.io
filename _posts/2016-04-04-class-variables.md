---
layout: post
title:  "Class Variables"
date:   2016-04-04 19:52:46 -0400
categories: snippets
---

These snippets are just a short reminder of how class variables work in Python. I understand this topic a bit too well, I think; I always remember the gotchas and can't remember which gotcha belongs to which important detail. I generally come up with the right answer then convince myself I'm wrong until I write a bit of code and experiment. Hopefully this snippet will shortcut that process.

Consider the following class hierarchy:

```python
from itertools import count


class Foo(object):

    counter = count()

    def __init__(self):
        self.id = self.counter.next()

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.id)


class Bar(Foo):
    pass


class Baz(Bar):
    pass
```

Every instance of `Foo` will be assigned a unique, automatically incrementing id using the `count` iterator for `itertools`. The thing to remember is that `Bar` and `Baz` are _also_ instances of `Foo`:

```python
>>> isinstance(Baz(), Foo)
True
```

Keep that in mind given the following code:

```python
>>> import random
>>> things = (Foo, Bar, Baz)
>>> for _ in xrange(10):
...     print random.choice(things)()
```

What is the expected result? If you said something like as follows:

```
Bar 0
Baz 1
Foo 2
Baz 3
Foo 4
Bar 5
Bar 6
Bar 7
Foo 8
Bar 9
```

Then you're on the right track.

The problem is that the code above is typically not what is meant by programmers. And while I typically come to the conclusion that what I'm actually expressing by the above code is counting instances of `Foo`, what I actually want to do is count instances of each class (how many of each `Foo`, `Bar`, and `Baz`).

Then I realize ... oh crap, I've strayed into metaprogramming land. And that's why I need the reminder of this post. I definitely get that I need a metaclass to make subclass counters work as expected, but I never remember exactly how to do it. So here's how.

```python
class Countable(type):

    def __new__(cls, name, bases, attrs):
        attrs['counter'] = count()
        return super(Countable, cls).__new__(cls, name, bases, attrs)


class Foo(object):

    __metaclass__ = Countable
```

Basically, what we've done here is is told the Foo class that it should be constructed using `Countable` instead of `type`. When the _class_ is created, therefore it is given the class attribute `counter`. Now the output is as follows:

```
Foo 0
Bar 0
Foo 1
Baz 0
Bar 1
Foo 2
Foo 3
Foo 4
Baz 1
Foo 5
```

This post isn't about a long discussion on the metaclass in Python or how `type` is a subclass of `type`, but simply serves as a reminder for the _very rare occasion_ that I have to rock something other than `type`. For more information on the subject, a very nice write-up, [A Primer on Python Metaclasses](https://jakevdp.github.io/blog/2012/12/01/a-primer-on-python-metaclasses/) by [@jakevdp](https://twitter.com/jakevdp) is the way to go. 
