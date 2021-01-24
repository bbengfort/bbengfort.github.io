---
categories: snippets
date: "2020-07-27T18:16:50Z"
title: Read mprofile Output into Pandas
---

When benchmarking Python programs, it is very common for me to use [`memory_profiler`](https://pypi.org/project/memory-profiler/) from the command line - e.g. `mprof run python myscript.py`. This creates a .dat file in the current working directory which you can view with `mprof show`. More often than not, though I want to compare two different runs for their memory profiles or do things like annotate the graphs with different timing benchmarks. This requires generating my own figures, which requires loading the memory profiler data myself.

I'm sure that the `memory_profiler` library probably has some utility functions to do this, but the simplest for me is to load things into a Pandas series. The `mprof` command keeps track of real timestamps, so in order to do comparisons, I have to reindex the time series based on the starting timestamp reference. The code snippet is as follows:


```python
import pandas as pd


def load_mprofile(path, name=None):
    ref = None
    times, values = [], []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith("CMDLINE"):
                if name is None:
                    name = line.rstrip("CMDLINE").strip()

            if line.startswith("MEM"):
                parts = line.split()
                val, ts = float(parts[1]), float(parts[2])
                if ref is None:
                    ref = ts

                times.append(ts-ref)
                values.append(val)

    return pd.Series(values, index=times, name=name)
```

Using this loader, I can compare two memory profiling sequences as follows:

```python
import os

import matplotlib.pyplot as plt


def plot_mprofiles(directory=".", ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(9,6))

    for name in os.listdir(directory):
        s = load_mprofile(os.path.join(directory, name))
        s.plot(ax=ax)

    ax.legend()
    return ax
```

Pretty straight forward, but a useful snippet to be able to lookup at a glance.