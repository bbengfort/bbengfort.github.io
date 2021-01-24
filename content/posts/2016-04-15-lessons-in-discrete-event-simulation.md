---
aliases:
- /observations/2016/04/15/lessons-in-discrete-event-simulation.html
categories: observations
date: '2016-04-15T06:26:42Z'
draft: false
showtoc: false
slug: lessons-in-discrete-event-simulation
title: Lessons in Discrete Event Simulation
---

Part of my research involves the creation of large scale distributed systems, and while we do build these systems and deploy them, we do find that simulating them for development and research gives us an advantage in trying new things out. To that end, I employ [discrete event simulation](https://en.wikipedia.org/wiki/Discrete_event_simulation) (DES) using Python's [SimPy](https://simpy.readthedocs.org/en/latest/) library to build very large simulations of distributed systems, such as the one I've built to inspect consistency patterns in variable latency, heterogenous, partition prone networks: [CloudScope](https://github.com/bbengfort/cloudscope).

Very briefly (perhaps I'll do a SimPy tutorial at another date), SimPy creates an environment that dispatches and listens for _events_. You create these event processes in the environment by implementing [generators]({% post_url 2016-02-05-iterators-generators %}) that `yield` control of the execution as they're working. As a result, the SimPy environment can call the `next()` method of your generator to do processing on schedule. Consider the following code:

```python
import simpy

def wake_and_sleep(env):
    state = 'Awake'

    while True:
        # change state and alert
        state = 'Awake' if state == 'Asleep' else 'Asleep'
        print "{} at {}".format(state, env.now)

        # wait 5 timesteps
        yield env.timeout(5)

if __name__ == '__main__':
    env = simpy.Environment()
    env.process(wake_and_sleep(env))
    env.run(until=100)
```

This simple generator function runs forever and constantly switches its state from `Awake` to `Asleep` to `Awake` again every 5 timesteps. If you run this you'll get something that looks as follows:

```text
Asleep at 0
Awake at 5
Asleep at 10
Awake at 15
Asleep at 20
...
```

The neat thing is that SimPy doesn't have a counter that simply increments the timestep and checks if any events have gone off -- and actually that's the whole point of discrete event simulation: to simulate events and their interactions as they occur in order without the burden of waiting for a real time simulation. Instead, SimPy has a master schedule that is created by calling the `next()` method of all its processes. When you `yield` a timeout of 5, your `next()` method will be called at `env.now + 5`. SimPy just increments `now` to the next timestep that has an event in it (or the minimum time of the current schedule).

This means that _it's a bad idea to constantly yield 1 timestep timeouts_. Especially if you're doing something like checking a state for work. Instead you should register a callback to the state change that you're looking for, and call the closure there. However, when you're modeling real world systems that do check their state every timestep, it's very difficult. This led me to the question:

**How bad is it to constantly yield 1 timestep timeouts in large simulations?**

So of course, we need data.

I created a SimPy process that would yield a timeout with a specific number of steps as a timeout, then track how many executions the process and the amount of real time that passes by. The experiment variables were the maximum number of timesteps allowed in the simulation and the number of steps to yield in the process. I selected a range of 10 maximum times between 1,000,000 and 50,000,000, with a stride of 5,000,000 and a range of steps between 1 and 10. This led to 100 runs of the simulation with each dimension pair. The [results]({{ site.baseurl }}assets/data/timestepping.csv) were as follows:

![Simulation Timestepping Results]({{ site.baseurl }}assets/images/2016-04-15-timestepping.png)

As you can see, there is an exponential decrease in the amount of real time taken by the system, and the amount of time you yield in your event process. Even just going from doing a check every single timestep to every other timestep will save you a lot of real time in your simulation process!

And a different view, the [interaction plot](https://stanford.edu/~mwaskom/software/seaborn/generated/seaborn.interactplot.html) is as follows:

![Simulation Interaction Plot]({{ site.baseurl }}assets/images/2016-04-15-interact-plot.png)

The interact plot shows every experiment, which is a grid of max simulation time (until) and the number of steps between event process yield. The heatmap shows that the amount of real time is exponentially dependent on steps (the curve around the X access) and linearly dependent on until (there is a straight line through the center of the curves).

The code to reproduce the data and the experiment is as follows:

{{< gist bbengfort f950dbc0ac9b7d3d4c32caf1d26dbcc5 >}}

The code does contain some cloudscope utilities, but they're not large and can be found in the [cloudscope repository](https://github.com/bbengfort/cloudscope).

For the results reported, the code was run on a MacBook Pro (Retina, 15-inch, Early 2013) with a 2.8 GHz Intel Core i7 processor and 16 GB of 1600 MHz DDR3 memory, running OS X El Capitan Version 10.11.4.

The visualizations were generated with the following code:

```python
import numpy as np
import pandas as pd
import seaborn as sns

# Set the context and style
sns.set_context('talk')
sns.set_style('whitegrid')

# Load the data
data = pd.read_csv('timestepping.csv')

# Plot the means of the experiment times by step.
sns.lmplot(
    'steps', 'time', size=12,
    x_estimator=np.mean, fit_reg=False, data=data
)

# Plot the interact plot of all experiments
sns.interactplot('steps', 'until', 'time', size=12, data=data)
```

So the lesson is - yield at least three timesteps in your simulation!
