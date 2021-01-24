---
categories: snippets
date: "2016-01-11T08:15:05Z"
title: Wrapping the Logging Module
---

The standard library `logging` module is excellent. It is also quite tedious if you want to use it in a production system. In particular you have to figure out the following:

1. configuration of the formatters, handlers, and loggers
2. object management throughout the script (e.g. the `logging.getLogger` function)
3. adding extra context to log messages for more complex formatters
4. handling and logging warnings (and to a lesser extent, exceptions)

The `logging` module actually does _all_ of these things. The problem is that it doesn't do them all at once for you, or with one single API. Therefore we typically go the route that we want to _wrap_ the logging module so that we can provide extra context on demand, as well as handle warnings with ease. Moreover, once we have a wrapped logger, we can do fun things like create mixins to put together classes that have loggers inside of them.

Below is a very typical example of a `logger.py` that we use in many of our projects. Note that the configuration is embedded into the module as a dictionary, but uses some configuration values from our settings object. The wrapper class simply takes a class based logger property, specified by `logging.getLogger` such that all instances uses the same logger. It then provides functions for the various levels, and a generic `log` method.

Note that if you `logger.warn` on a logger with `raise_warnings=True`, then it will kick out to the `warnings` module. Finally I provide a mixin class for providing loggers on demand as properties.

{{< gist bbengfort 782d4e64d75b1dce77ee >}}

The thing I still haven't figured out is how to put the configuration easily into a YAML file, particularly while using [Confire](https://pypi.python.org/pypi/confire/0.2.0). This is what led to putting the configuration dictionary directly into the utility module as seen above. The primary problem is that unless I create classes for every nested level of the logging configuration, by adding _anything_ to the YAML file you blow away the other keys. I think that I'll have to create a `LoggingConfiguration` type thing in Confire specifically, and figure it out there.
