---
categories: snippets
date: "2016-02-16T07:24:04Z"
title: Implementing the Observer Pattern with an Event System
---

I was looking back through some old code (hoping to find a quick post before I got back to work) when I ran across a project I worked on called Mortar. Mortar was a simple daemon that ran in the background and watched a particular directory. When a file was added or removed from that directory, Mortar would notify other services or perform some other task (e.g. if it was integrated into a library). At the time, we used Mortar to keep an eye on FTP directories, and when a file was uploaded Mortar would move it to a staging directory based on who uploaded it, then do some work on the file.

Mortar was a specific implementation of the [_observer design pattern_](http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Observer.html). And while it might seem that this means that Mortar was observing the directory, in fact Mortar was the thing being observed, which for the purposes of a design pattern discussion we will call the _subject_ (or something that implements the _observable_ interface in Java terms). The _observers_ were actually the things that did work when Mortar noticed a change in the file system; e.g. add something to a directory, move the file, do some work on the file, etc.

[![Observer Design Pattern](/images/2016-02-16-observer.png)](/images/2016-02-16-observer.png)

Ok, so a brief note on the observer pattern, which you should read about somewhere that is not here (like in the link above). The basic pattern is that we have a _subject_ that contains some state. Other objects called _observers_ register themselves with the subject and ask to be notified when the state changes. There are a couple of ways to implement this, but the most common is to give the observers a method called `update`. When the state changes on the subject, it simply calls the `update` method for each observer in the order that they registered.

Of course, this brings up a whole host of other issues like [synchronization](http://effbot.org/zone/thread-synchronization.htm) or [side-effects](https://clusterhq.com/2014/05/15/isolating-side-effects-state-machines/). Like I said, explore this pattern in detail! But back to the code snippet I rediscovered.

Coming from an event oriented programming environment like JavaScript or ActionScript, the observer pattern is very easy to understand. In this case the subject is whatever is listening to user actions like mouse clicks or key presses. Rather than calling a single `update` function on all the observers; observers register callbacks (callables like functions or callable classes) to specific event types. Events themselves are are also data, and contain information that is passed to the callback function. Way back in 2010, I wanted to bring this style of event dispatcher to my Python programming, so with some inspiration from [Python Event Dispatcher](http://labs.makemachine.net/2010/04/python-event-dispatcher/) by [@makemachine](https://twitter.com/makemachine), I came up with the following:

{{< gist bbengfort b5c059e352b3b04cfc4d >}}

The idea here is that you would create (or subclass) the event dispatcher, and then have observers register their callbacks with specific event types (or multiple event types if needed). Event types in this case are just strings that can be compared, and I've provided several examples as static variables on the `Event` class itself. The dispatcher guarantees that when an event occurs, all (and only) callbacks that are registered at the time of the event will receive an unmodified copy of the event, no matter the order of their registration. It does this through the `deepycopy` and `clone` functions.

While this is not fundamentally different than the observer pattern, it does implement things in a style that I think other data scientists may understand, particularly if they do JavaScript for visualization. Moreover, I like the idea of having multiple event types and passing state through a packet.

In order to make this thread safe, some mutex would need to be added to the dispatcher class. If you're willing to make that happen, I'd love to see it!
