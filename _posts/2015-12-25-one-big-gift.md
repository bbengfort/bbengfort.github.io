---
layout: post
title:  "One Big Gift Selection Algorithm"
date:   2015-12-25 11:54:12 -0500
categories: snippets reminders
---

My family does "one big gift" every Christmas; that is instead of everyone simply buying everyone else a smaller gift; every person is assigned to one other person to give them a single large gift. Selection of who gives what to who is a place of some (minor) conflict. Therefore we simply use a random algorithm. Unfortunately, apparently a uniform random sample of pairs is not enough, therefore we take 100 samples to vote for each combination to see who gets what as follows:

```python
from random import shuffle
from collections import Counter
from itertools import combinations
from collections import defaultdict


def random_combinations(items, iterations=100):
    """
    Randomly combines items until a group reaches the minimum number
    of votes. This function will yield both the item voted for and
    the # of votes.
    """

    votes   = defaultdict(Counter)
    giftees = set([])

    for idx in xrange(iterations):
        shuffle(items)
        for (giver, giftee) in combinations(items, 2):
            votes[giver][giftee] += 1

    combos  = []
    for giver, votes in votes.iteritems():
        for giftee, vote in votes.most_common():
            if giftee not in giftees:
                combos.append((giver, giftee, vote))
                giftees.add(giftee)
                break

    if len(combos) != len(items):
        return random_combinations(items, iterations)

    return combos


def read_names(path):
    """
    Reads the names from the associated text file (newline
    delimited). There must be an even number of names otherwise
    this won't work very well.
    """
    with open(path, 'r') as f:
        return [
            name.strip() for name in f if name.strip()
        ]


if __name__ == '__main__':
    # Print the names and the votes!
    for data in random_combinations(read_names('names.txt')):
        print "{} --> {} ({} votes)".format(*data)
```

## Follow Ups

- The (secret) [Gist](https://gist.github.com/bbengfort/4df612b0155ca2a362ae) contains all the code including the data file.
- Need to implement a method that does not allow for repeat giftee pairs. 
