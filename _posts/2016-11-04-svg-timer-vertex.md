---
layout: post
title:  "SVG Vertex with a Timer"
date:   2016-11-04 10:30:29 -0400
categories: snippets
---

In order to promote the use of graph data structures for data analysis, I've recently given talks on [dynamic graphs](https://youtu.be/RgixxVpfXDY): embedding time into graph structures to analyze change. In order to embed time into a graph there are two primary mechanisms: make time a graph element (a vertex or an edge) or have multiple subgraphs where each graph represents a discrete time step. By using either of these techniques, opportunities exist to perform a structural analysis using graph algorithms on time; for example - asking what time is most central to a particular set of relationships.

Graphs are primarily useful to simplify modeling and querying, but they are also useful for visual analytics. While visualizing static graphs with time embedded as a structure requires only standard graph techniques, visualizing dynamic graphs requires some sort of animation or interaction. We are currently exploring these techniques in the District Data Labs dynamic graphs research group. Towards that research, we are proposing to use D3 and SVG for interaction and visualization.

As time moves forward graph elements (vertices and edges) will change, either being added to the graph or removed from them. To support visual analytics, particularly with layouts that will change depending on the nodes that get added (like force directed layouts), these transitions must not be sudden, but instead give visual clues as to what's going on in the layout. The most obvious choice is to use opacity or size to fade in and out during the transition. However, this does not give the user any sense of how long the node has been on the screen, or how long it has left.

Therefore, I'm interested in creating vertices that have timers associated with them. Inspired by [raftscope](https://raft.github.io/raftscope-replay/), I want to create vertices that have a timer that indicates how long they've been on the screen. Here is my initial attempt:

<style type="text/css">

    svg {
        width: 100%;
        height: 120px;
    }

    svg .vertex text {
      text-anchor: middle;
      dominant-baseline: central;
      text-align: center;
      fill: #FEFEFE;
    }

    svg .vertex circle {
        fill: #003F87;
    }

    svg .vertex path {
      fill: none;
      stroke: #CF0000;
    }


</style>

<svg id="timer-vertex"></svg>

<script
  src="https://code.jquery.com/jquery-3.1.1.slim.min.js"
  integrity="sha256-/SIrNqv8h6QGKDuNoLGA4iret+kyesCkHGzVUUV0shc="
  crossorigin="anonymous"></script>

<script type="text/javascript">

    var SVG = function(tag) {
        return $(document.createElementNS('http://www.w3.org/2000/svg', tag));
    };

    var ARC_WIDTH = 6;

    function circleCoord(frac, cx, cy, r) {
        var radians = 2 * Math.PI * (0.75 + frac);
        return {
            x: cx + r * Math.cos(radians),
            y: cy + r * Math.sin(radians),
        };
    }

    function arcSpec(spec, fraction) {
        var radius = spec.r + ARC_WIDTH/2;
        var end = circleCoord(fraction, spec.cx, spec.cy, radius);
        var s = ['M', spec.cx, ',', spec.cy - radius];

        if (fraction > 0.5) {
            s.push('A', radius, ',', radius, '0 0,1', spec.cx, spec.cy + radius);
            s.push('M', spec.cx, ',', spec.cy + radius);
        }
        s.push('A', radius, ',', radius, '0 0,1', end.x, end.y);
        return s.join(' ');
    }

    function updateArcTimer(elems, spec, current) {
        var amt = current - 0.015;
        if (amt < 0) {
            amt = 1.0;
        }

        elems.attr('d', arcSpec(spec, amt));
        setTimeout(function() { updateArcTimer(elems, spec, amt) }, 100);
    }

    $(document).ready(function() {

        var svg = $("#timer-vertex");

        vertexSpec = {
            cx: svg.width() / 2,
            cy: svg.height() / 2,
            r: 36,
        }

        // Create the vertex
        svg.append(
            SVG('g')
                .attr('id', 'vertex-1')
                .attr('class', 'vertex')
                .append(SVG('a')
                    .append(SVG('circle')
                                .attr('class', 'background')
                                .attr(vertexSpec))
                    .append(SVG('path')
                                .attr('class', 'timer-arc')
                                .attr('style', 'stroke-width: ' + ARC_WIDTH)
                                .attr('d', arcSpec(vertexSpec, 1.0)))
                )
                .append(SVG('text')
                            .attr('class', 'vlabel')
                            .text('v1')
                            .attr({x: vertexSpec.cx, y: vertexSpec.cy}))
        );

        // Animate the timer
        updateArcTimer($(".timer-arc"), vertexSpec, 1.0);

    });

</script>

The code to do this uses JavaScript with jQuery as well as CSS but no other libraries. To make this work for graphs, we'll have to find a way to implement this vertex type in D3. But for now, we can just look what's happening.

First I added an SVG element to the body of my HTML:

```html
<html>
    <head>
        <title>Vertex Timer Test</title>
    </head>
    <body>
        <svg id="timer-vertex"
             xmlns="http://www.w3.org/2000/svg" version="1.1"
             xmlns:xlink="http://www.w3.org/1999/xlink">
        </svg>
    </body>
</html>
```

Then add some simple styles with CSS so that you don't have to manually set them on every single element:

```css
svg {
    width: 100%;
    height: 120px;
}

svg .vertex text {
  text-anchor: middle;
  dominant-baseline: central;
  text-align: center;
  fill: #FEFEFE;
}

svg .vertex circle {
    fill: #003F87;
}

svg .vertex path {
  fill: none;
  stroke: #CF0000;
}
```

For the rest of the work, we're going to manually add SVG elements with JavaScript, updating their attributes with computed values. To make this easier, a simple function will allow us to create SVG elements in the correct namespace:

```javascript
function SVG(tag) {
    var ns = 'http://www.w3.org/2000/svg';
    return $(document.createElementNS(ns, tag));
}
```

We can now use this function to quickly create the elements of our vertex: the circle representing the node, the text representing the label, and the arc representing the timer. First, let's find the center of the SVG so that we know where to place the vertex, and define other properties like its radius.

```javascript
// Set the constant arc width
var ARC_WIDTH = 6;

// Select the svg to place the vertex into
var svg = $("#timer-vertex");

// Define the vertex center point and radius
vertexSpec = {
    cx: svg.width() / 2,
    cy: svg.height() / 2,
    r: 30,
}
```

Before we can add all of the elements, we need to define the method by which we create the arc. To do this we're going to create a `path` that [follows an arc](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths#Arcs). Creating paths with SVG means defining a `d` attribute, which contains a series of commands and parameters that define the shape of the path. The first command is the "move to" command, `M`, that specifies where the path begins, e.g. `M50 210` places a point at the coordinates `(50, 210)`. We then define the arc with the `A` command. The `A` command is complex, you have to define the x and y radius, axis rotation, sweep flags and an endpoint. However, it is powerful.

In the next snippet we will use the `arcSpec` function to create the `d` attribute for our path. It returns a string from the spec defining the vertex (the center and radius) as well as the fraction of the circle we want represented on the arc. It also uses another helper function, `circleCoord` to determine where points around the circle are located.

```javascript
function circleCoord(frac, cx, cy, r) {
    var radians = 2 * Math.PI * (0.75 + frac);
    return {
        x: cx + r * Math.cos(radians),
        y: cy + r * Math.sin(radians),
    };
}

function arcSpec(spec, fraction) {
    var radius = spec.r + ARC_WIDTH/2;
    var end = circleCoord(fraction, spec.cx, spec.cy, radius);
    var s = ['M', spec.cx, ',', spec.cy - radius];

    if (fraction > 0.5) {
        s.push('A', radius, ',', radius, '0 0,1', spec.cx, spec.cy + radius);
        s.push('M', spec.cx, ',', spec.cy + radius);
    }
    s.push('A', radius, ',', radius, '0 0,1', end.x, end.y);
    return s.join(' ');
}
```

Now that we have these two helper functions in place, we can finally define our elements:

```javascript
svg.append(
    SVG('g')
        .attr('id', 'vertex-1')
        .attr('class', 'vertex')
        .append(SVG('a')
            .append(SVG('circle')
                        .attr('class', 'background')
                        .attr(vertexSpec))
            .append(SVG('path')
                        .attr('class', 'timer-arc')
                        .attr('style', 'stroke-width: ' + ARC_WIDTH)
                        .attr('d', arcSpec(vertexSpec, 1.0)))
        )
        .append(SVG('text')
                    .attr('class', 'vlabel')
                    .text('v1')
                    .attr({x: vertexSpec.cx, y: vertexSpec.cy}))
);
```

This is simply a matter of appending various SVG elements together to create the group of shapes that together make up the vertex.

Now to animate, I'll simply recompute the path of the ARC for a smaller fraction of the vertex at each time step. To do this I'll use a function that updates the path, then uses `setTimeout` to schedule the next update once it's complete:

```javascript
function updateArcTimer(elems, spec, current) {
    var amt = current - 0.015;
    if (amt < 0) {
        amt = 1.0;
    }

    elems.attr('d', arcSpec(spec, amt));
    setTimeout(function() { updateArcTimer(elems, spec, amt) }, 100);
}
```

Playing around with the delay between update (100 ms in this example) and the amount of the arc to reduce (0.015 in this example) changes how fast and smooth the timer is. However, making it too granular can cause weird jitters and artifacts to appear. Kick this function off right after creating the vertex as follows:

```javascript
updateArcTimer($(".timer-arc"), vertexSpec, 1.0);
```

Future work for this project will be to implement this style vertex with D3, and the ability to set timers with a meaningful time measurement. I'd also like to look into other styles, for example the circle fill emptying out (like a sand timer) at the rate of the timer or the halo of the vertex flashing slowly or more quickly as it moves to the end of the timer. Importantly, these elements should also be able to be paused and hooked into other update mechanisms, such that sliders or other interactive functionality can be used. Finally, I'm not sure how edges will interact with the timer halo, but it is also important to consider.
