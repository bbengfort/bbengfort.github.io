---
title: "Dynamics in Graph Analysis Adding Time as a Structure for Visual and Statistical Insight"
slug: "dynamics-in-graph-analysis-adding-time-as-a-structure-for-visual-and-statistical-insight"
date: "2016-10-24T12:00:00-05:00"
draft: false
categories: presentations
showtoc: false
---

I gave this talk twice, both at [PyData DC](http://pydata.org/dc2016/schedule/presentation/36/) on October 24, 2016 and at [PyData Carolinas](http://pydata.org/carolinas2016/schedule/presentation/39/) on September 15, 2016. Both videos are below if you feel like figuring out which presentation was better!

### PyData DC

{{< youtube QhMZ1PmlJn4 >}}

### PyData Carolinas

{{< youtube RgixxVpfXDY >}}

### Slides

{{< slideshare id="66065281" >}}

### Description

Network analyses are powerful methods for both visual analytics and machine learning but can suffer as their complexity increases. By embedding time as a structural element rather than a property, we will explore how time series and interactive analysis can be improved on Graph structures. Primarily we will look at decomposition in NLP-extracted concept graphs using NetworkX and Graph Tool.

Modeling data as networks of relationships between entities can be a powerful method for both visual analytics and machine learning; people are very good at distinguishing patterns from interconnected structures, and machine learning methods get a performance improvement when applied to graph data structures. However, as these structures become more complex or embed more information over time, both visual and algorithmic methods get messy; visual analyses suffer from the "hairball" effect, and graph algorithms require either more traversal or increased computation at each vertex. A growing area to reduce this complexity and optimize analytics is the use of interactive and subgraph techniques that model how graph structures change over time.

In this talk, I demonstrate two practical techniques for embedding time into graphs, not as computational properties, but rather as structural elements. The first technique is to add time as a node to the graph, which allows the graph to remain static and complete, but minimizes traversals and allows filtering. The second is to represent a single graph as multiple subgraphs where each is a snapshot at a particular time. This allows us to use time series analytics on our graphs, but perhaps more importantly, to use animation or interactive methodologies to visually explore those changes and provide meaningful dynamics.

