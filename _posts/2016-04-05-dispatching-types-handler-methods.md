---
layout: post
title:  "Dispatching Types to Handler Methods"
date:   2016-04-05 08:58:32 -0400
categories: snippets
---

A while I ago, I discussed the [observer pattern]({% post_url 2016-02-16-observer-pattern %}) for dispatching events based on a series of registered callbacks. In this post, I take a look at a similar, but very different methodology for dispatching based on type with pre-assigned handlers. For me, this is actually the more common pattern because the observer pattern is usually implemented as an API to outsider code. On the other hand, this type of dispatcher is usually a programmer's pattern, used for development and decoupling.

For example, the project I'm currently working on involves replica servers handling remote procedure calls (RPCs) from remote servers. Each RPC is basically a typed packet of specific data, much like the arguments you would pass to a function. It's completely intended for one single procedure on the local server. I treat RPCs as events because I research distributed systems (and messages are events, but more on that later) and so each replica server needs to route (dispatch) the RPC event to the correct handler.

However, when you're programming -- you're basically naming things. So the question is, why create a mapping of message types to handlers _when you already have the name of the event_? Isn't there some way to do this automatically? The answer is, yes of course there is. This gives you the following benefits:

1. Easy extensibility: create an event type and handler with the same name.
2. No magic strings that may be typo'd!
3. Single point of dispatch, no need to subclass your routing.
4. A clear and understandable API for future you.

So the strategy is to create _types_ (classes for the point of this discussion) that can be identified by name. Then create a dispatcher that uses that name, automatically looks up the appropriate handler based on that name, and calls it. The code to do so is as follows:

<script src="https://gist.github.com/bbengfort/6e2de9abe41ac02ee827a94c1ff3e6a9.js"></script>

Ok, so there are a couple of extra things here, specifically the need to do things in [PEP8 naming style](https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles). The type names should be in [`CamelCase`](https://en.wikipedia.org/wiki/CamelCase) while the method names should be in [`snake_case`](https://en.wikipedia.org/wiki/Snake_case). It's not trivial to put together helper functions to transform strings to camel case, or to snake case. You can use generators, string processing, regular expressions, transformers, and more.

In the snippet I've included the methods that I prefer (using regular expressions that are compiled in advance for performance). Moreover, since this is so common to add to code, I've not only included a downloadable Gist of the code, but also tests so that you can easily add it to your code base. 
