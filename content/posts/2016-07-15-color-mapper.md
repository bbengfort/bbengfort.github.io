---
aliases:
- /snippets/2016/07/15/color-mapper.html
categories: snippets
date: '2016-07-15T16:28:11Z'
draft: false
showtoc: false
slug: color-mapper
title: Color Map Utility
---

Many of us are spoiled by the use of matplotlib's [colormaps](http://matplotlib.org/examples/color/colormaps_reference.html) which allow you to specify a string or object name of a color map (e.g. `Blues`) then simply pass in a range of nearly continuous values which are spread along the color map. However, using these color maps for categorical or discrete values (like the colors of nodes) can pose challenges as the colors may not be distinct enough for the representation you're looking for.

Color is a very interesting topic, and I'm very partial to the work of [Cynthia Brewer](http://colorbrewer2.org/) who suggests color scales for maps in particular that are understandable even by those who are color blind. D3 makes very heavy use of the Brewer palettes and provides [Every ColorBrewer Scale](https://bl.ocks.org/mbostock/5577023) as a JSON file. Unfortunately Python doesn't natively have ColorBrewer in any of it's projects (with the notable exception of [seaborn](https://stanford.edu/~mwaskom/software/seaborn/)).

XKCD also did a [color survey](https://blog.xkcd.com/2010/05/03/color-survey-results/) and Nathan Yao also has a lot to say about [color on Flowing Data](https://flowingdata.com/tag/color/). Color is hugely important, and we shouldn't just be forced to stick with the status quo. We should make things with awesome colors. I like to use tools like [Paletton](http://paletton.com/) and [Color Lovers](http://www.colourlovers.com/palettes) to get unique palettes for my projects.

So you need something like the colormap in order to actually use these things. Therefore, for descrete values, I give you the `ColorMap`:

{{< gist bbengfort 1973e6b017eefe39e041990451f9643a >}}

So how do you use this tool? First you instantiate the object with either a list of colors or one of the names I provided in the script (and expand your script with your own names!). You then have a callable object that you can get the color for any hashable object. The `ColorMap` retains the color information and raises an exception if you ask for more colors than you have in the map.

```python
>>> cmap = Colors('flatui')
>>> cmap('A')
#9b59b6
>>> cmap('B')
#3498db
>>> cmap('A')
#9b59b6
```

You can then use this tool in Graph Tool graphs or other utilities. For example, here is some standard graph tool code that I use to visualize graphs:

```python
import graph_tool.all as gt

# Draw the vertices with labels using their name property
# and their size according to their degree.
vlabel  = G.vp['name']
vsize   = G.degree_property_map("in")
vsize   = gt.prop_to_size(vsize, ma=60, mi=20)

# Set the vertex color using the color map and the flatui scheme.
vcolor  = G.new_vertex_property('string')
vcmap   = ColorMap('flatui', shuffle=False)

# Add the color from the 'type' property of the vertex.
for vertex in G.vertices():
    vcolor[vertex] = vcmap(G.vp['type'][vertex])

# Set the edge color using the set1 colorbrewer scale
ecolor  = G.new_edge_property('string')
ecmap   = ColorMap('set1', shuffle=False)

# Add the color from the 'label' property of the edge.
for edge in G.edges():
    ecolor[edge] = ecmap(G.ep['label'][edge])

# Label the edge and size it according to the norm and weight
elabel  = G.ep['label']
esize   = G.ep['norm']
esize   = gt.prop_to_size(esize, mi=.1, ma=3)
eweight = G.ep['weight']

# Draw the graph!
gt.graph_draw(
    G, output_size=(1200,1200), output=os.path.join(FIGURES, name),
    vertex_text=vlabel, vertex_size=vsize, vertex_font_weight=1,
    vertex_pen_width=1.3, vertex_fill_color=vcolor,
    edge_pen_width=esize, edge_color=ecolor, edge_text=elabel
)
```

And there you have it, put colors everywhere.
