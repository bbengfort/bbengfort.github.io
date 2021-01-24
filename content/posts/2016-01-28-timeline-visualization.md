---
aliases:
- /snippets/2016/01/28/timeline-visualization.html
categories: snippets
date: '2016-01-28T22:24:47Z'
draft: false
showtoc: false
slug: timeline-visualization
title: Timeline Visualization with Matplotlib
---

Several times it's come up that I've needed to visualize a time sequence for a collection of events across multiple sources. Unlike a normal time series, events don't necessarily have a _magnitude_, e.g. a stock market series is a graph with a time and a price. Events simply have times, and possibly types.

A one dimensional number line is still interesting in this case, because the frequency or density of events reveal patterns that might not easily be analyzed with non-visual methods. Moreover, if you have multiple sources, overlaying a timeline on each can show which is busier, when and possibly also demonstrate some effect or causality.

![Timeline Plot](/images/2016-01-28-timeline.svg)

The timelines plot above shows what I mean. Here I have five sensors that can observe different events: red, green, and blue. Each sensor records the time it sees the event from an initial time, zero along with the type and source. To plot this, I simply used [Matplotlib](http://matplotlib.org/) to create a scatterplot where the `y` value was simply the index of the sensor in a sorted list. Some careful axis hacking led to the result.

The script and a sample of the dataset follow:

{{< gist bbengfort 0938048f364a8c0d6ae3 >}}

Obviously this function is very dataset dependent, though I tried to make it as generic as possible. Still it serves as a guide to create these kind of plots. Again, this is something I've copy and pasted from former code at least twice now, so it's good to have it in one place!
