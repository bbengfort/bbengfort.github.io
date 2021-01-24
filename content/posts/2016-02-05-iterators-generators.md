---
categories: programmer
date: "2016-02-05T22:47:15Z"
title: Iterators and Generators
---

This post is an attempt to explain what iterators and generators are in Python, defend the `yield` statement, and reveal why a library like [SimPy](https://simpy.readthedocs.org/en/latest/) is possible. But first some terminology (that specifically targets my friends who Java). _Iteration_ is a syntactic construct that implements a loop over an _iterable_ object. The `for` statement provides _iteration_, the `while` statement may provide iteration. An _iterable_ object is something that implements the _iteration protocol_ (Java folks, read interface). A _generator_ is a function that produces a sequence of results instead of a single value and is designed to make writing _iterable_ objects easier.

## Iterables

Iterable objects are constructed by the built-in function, `iter`, which takes an iterable object and returns an iterator. The Python [data model](https://docs.python.org/2/reference/datamodel.html) allows you to define custom objects that implement double underscore methods related to the built-in functions and operators. Therefore if you implement an object with an `__iter__` method, your object can be passed to the `iter` built-in.

The `__iter__` method must return an iterable object, which if it is the same object, can simply return `self`. Iterable objects must have a `next` method that is called on every pass of the loop. When iteration is complete, the `next` method should raise `StopIteration`. Here is an example of a Dealer iterator that shuffles a deck of cards on `iter` then deals out cards on each call of next, until there are no more cards left in the deck:

{{< gist bbengfort b0596990db96b6a7aa82 >}}

The thing to note here is that the object keeps track of its own state, through it's own pointer value (the "shoe"). This means that the iterable can be "exhausted" without returning any more data. Try the following and see what happens:

```python
dealer = Dealer()
for card in dealer:
    for card in dealer:
        print card
```

Note that I also used the shorthand and didn't call the `iter` function directly, but let the syntax of the for loop handle it for me. Also note that other built-in functions consume iterables like `list` which will take the contents of the iterable and store it in memory in a list, or `enumerate` which will also provide an index of each value in the iterator.

## Generators

Generators are designed to allow you to easily create iterables without having to deal with the iterator interface. Instead you can create a function that does not `return` but rather `yield` values. When the `yield` keyword is used inside a function, a generator is immediately returned that has a `next` method. Look how simple our dealer is using a generator function:

```python
def dealer():
    cards = [
        u"{: >2}{}".format(*card)
        for card in zip(FACES * len(SUITS), SUITS * len(FACES))
    ]
    random.shuffle(cards)
    for card in cards:
        yield card
```

The generator allows us to forget about how to implement an iterable, keep track of state, etc. which greatly simplifies the process. You can get access to the generator directly from the function:

```python
dealer_generator = dealer()
print dealer_generator.next()
```

Or you can simply loop over the function as we've been doing so far:

```python
for card in dealer():
    print card
```

The `yield` statement is often mistaken for yielding a value instead of simply returning one. What the generator is actually doing is yielding the execution context back to the caller. Whenever the caller calls `next()` on the generator, the execution is returned directly to the line where the yield was executed. Consider the following example:

```python
def surround(n):
    for idx in xrange(n):
        print "above {}".format(idx)
        yield idx
        print "below {}".format(idx)

for idx in surround(4):
    print "around {}".format(idx)
```

You get output that appears as follows:

```text
above 0
around 0
below 0
above 1
around 1
below 1
above 2
around 2
below 2
above 3
around 3
below 3
```

What is happening here? On the `for` loop call, a generator is returned, the "above" print statement happens, then control is yielded to the executing context, which prints "around". That block complete, the loop continues, going to the next cycle, and calls next on the generator, which returns control right after the yield, printing the "below" statement, continuing to the next "above" then yielding, so on and so forth.

## SimPy and Context

Generators are incredibly handy for things like comprehensions, memory safe iteration, reading from multiple files simultaneously, and more. However, I want to talk about their ingenious use in the discrete event simulation library, SimPy.

SimPy allows you to create processes which are essentially generators. These processes can run forever, but they must `yield` events that occur in the simulation. One very important event is the `timeout` event that allows time to pass in the simulation. So how would we implement a simple SimPy environment using generators? Consider a blinking light generator:

```python
def blinker(env):
    while True:
        print 'Blink at {}!'.format(env.now)
        yield 5
```

The desired effect is that this prints "Blink" every 5 time steps in the simulation (env in this case is just a SimPy environment). The offset allows us to start blinking lights that blink at different times. Note that this `while` loop doesn't terminate, so if we just hit go on this thing, even if we manage to wait 5 (however we do that) then this will go forever, how do we cancel it? Moreover, how do we cancel multiple blinking lights?

Basically what we can do is we can simply manage the generators for our simulation and call `next` on them when appropriate, and if we want to terminate, then simply don't call their next method. Here is a [simple implementation](https://gist.github.com/bbengfort/dc2aea53d4ca7fdef925):

```python
from collections import defaultdict

class BlinkerEnvironment(object):

    def __init__(self, blinkers=4):
        self.now = 0
        self.blinkers = defaultdict(list)
        for idx in xrange(blinkers):
            # schedule blinkers by offset
            self.blinkers[idx].append(blinker(self))

    def run(self, until=100):
        while self.now < until:

            if self.now in self.blinkers:

                for blinker in self.blinkers.pop(self.now):
                    timeout = blinker.next() + self.now
                    self.blinkers[timeout].append(blinker)

            self.now = min(self.blinkers.keys())
```

As you can see in this code, the blinkers dictionary is a list of blinkers keyed to the time value that they are supposed to be called again. The environment keeps track of the current timestamp, and initializes 4 blinkers that are offset so that the blinkers aren't all blinking at the same time.

The `run` method is passed an `until` argument, which limits how long the simulation goes on. If the current timestamp is in the blinkers schedule, then we go and fetch all the generators for the now value, then call their next method. We reschedule the blinker based on the timeout number that it yields to us, then we increment now by the next scheduled blink to take place (skipping over time steps that don't matter is what gives discrete event simulation its desired properties). And voila, we've implemented a simple simulation using generators!
