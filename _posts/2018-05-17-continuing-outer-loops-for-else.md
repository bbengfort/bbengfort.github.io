---
layout: post
title:  "Continuing Outer Loops with for/else"
date:   2018-05-17 09:02:43 -0400
categories: snippets
---

When you have an outer and an inner loop, how do you continue the outer loop from a condition inside the inner loop? Consider the following code:

```python
for i in range(10):
    for j in range(9):
        if i <= j:
            # break out of inner loop
            # continue outer loop
        print(i,j)

    # don't print unless inner loop completes,
    # e.g. outer loop is not continued
    print("inner complete!")
```

Here, we want to print for all `i` &isin; `[0,10)` all numbers `j` &isin; `[0,9)` that are less than or equal to i and we want to print complete once we've found an entire list of `j` that meets the criteria. While this seems like a fairly contrived example, I've actually encountered this exact situation in several places in code this week, and I'll provide a real example in a bit.

My first instinct simply uses a function to use `return` to do a "hard break" out of the loop. This allows us to short-circuit functionality by exiting the function, but doesn't actually provide `continue` functionality, which is the goal in the above example. The technique does work, however, and in multi-loop situations is probably the best bet.

```python
def inner(i):
    for j in range(9):
        if i <= j:
            # Note if this was break, the print statement would execute
            return
        print(i,j)

    print("inner complete")

for i in range(10):
    inner(i)
```

Much neater, however is using `for/else`. The `else` block fires iff the for loop it is connected with _completes_. This was very weird to me at first, I thought `else` should trigger if `break`. Think of it this way though:

> You're searching through a list of things, `for item in collection` and you plan to `break` when you've found the item you're looking for, `else` you do something if you exhaust the collection and didn't find what you were looking for.

Therefore we can code our loop as follows:

```python
for i in range(10):
    for j in range(9):
        if i <= j:
            break
        print(i,j)
    else:
        # Outer loop is continued
        continue

    print("inner complete!")
```

This is a little strange, because it is probably more appropriate to put our `print` in the `else` block, but this was the spec, continue the outer loop if the inner loop gets broken.

Here's a better example with date parsing:

```python
# Try to parse a timestamp with a bunch of formats
for fmt in (JSON, PG, ISO, RFC, HUMAN):
    try:
        ts = datetime.strptime(ts, fmt)
        break
    except ValueError:
        continue
else:
    # Could not parse with any of the formats required
    raise ValueError("could not parse timestamp")
```

Is this better or worse than the function version of this?

```python
def parse_timestamp(ts):
    for fmt in (JSON, PG, ISO, RFC, HUMAN):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue

    raise ValueError("could not parse timestamp")

ts = parse_timestamp(ts)
```

Let's go to the benchmarks:

![Benchmark for/else vs. function date parsing]({{site.base_url }}/assets/images/2018-05-17-benchmark.png)

So basically, there is no meaningful difference, but depending on the context of implementation, using `for/else` may be a bit more meaningful or easy to test than having to implement another function.

Benchmark code can be found [here](https://gist.github.com/bbengfort/bc7f985b2b18d789a30d8a52145aed8b).
