---
categories: tutorials
date: "2016-01-23T08:46:18Z"
title: Building a Console Utility with Commis
---

Applications like [Git](https://git-scm.com/) or [Django's management utility](https://docs.djangoproject.com/en/1.9/ref/django-admin/) provide a rich interaction between a software library and their users by exposing many subcommands from a single root command. This style of what is essentially better argument parsing simplifies the user experience by only forcing them to remember one primary command, and allows the exploration of the utility hierarchy by using `--help` and other visibility mechanisms. Moreover, it allows the utility writer to decouple different commands or actions from each other.

And, this is actually not very hard to do, as shown in [&ldquo;Simple CLI Script with Argparse&rdquo;]({% post_url 2016-01-10-simple-cli-argparse %}), the `argparse` module in the standard library will allow you to create subparsers. By setting a default &ldquo;handling&rdquo; function associated with each subparser, you can simply execute different functions with different arguments from the command line. Unfortunately, while easy, the _organization_ and _definition_ of the utility quickly gets out of control, particularly as the `argparse.add_argument` method is so verbose.

Enter [Commis](https://github.com/bbengfort/commis), a library designed to make define and organizing complex command line utilities easier. Commis was inspired by the Django management utility, and was written specifically to provide similar functionality and code organization in other projects. The design principles are simple:

1. Maintain console commands inside of a library.
2. Define arguments simply and extensibly (with better formatting).
3. Easily and automatically add commands to the console utility.
4. Decouple the execution context (argument parsing, output).
5. Compose the most simple executable script possible.

In this tutorial we will see how to build a console utility using Commis. This tutorial is applicable both to user facing console tools (e.g. Git) or library specific tools (e.g. django-admin). We will focus on organization and package management rather than the details of writing command code, as this is where Commis shines. For the purposes of this tutorial, we will consider the building of a console utility that acts like a static site generator and has two primary commands: `build` and `serve`.

## Code Organization

One of the most important things to understand about Commis is how to organize larger projects in order to manage complex utilities. In our tutorial example we are creating a static site generator called `foo` with two commands, `build` and `serve`. Following the basic template for a Python project, a very simple organization for `foo` would be as follows:

```
$ project
.
├── foo
|   ├── __init__.py
|   ├── console
|   |   ├── commands    
|   |   |   ├── __init__.py
|   |   |   ├── build.py
|   |   |   └── serve.py
|   |   ├── __init__.py
|   |   └── app.py
├── foo-app.py
├── LICENSE.txt
├── README.md
├── requirements.txt
└── setup.py
```

Our primary code base is in the `foo` library, which should hold 99% of the Python code. The only other Python modules in this example that are outside of the `foo` library are `foo-app.py` and `setup.py`. The `foo-app.py` script is the main entry point for our application and is very simple, which we will see shortly. The `setup.py` script is for packaging and distribution via `pip`, which will will also discuss in a bit.

The `foo` package includes a `foo.console` module, which in turn contains a `foo.console.commands` and `foo.console.app` modules. The `app` module will contain a subclass of `commis.ConsoleProgram`, which defines how our console application should behave. The `commands` module will organize our various subcommands, and as you can see, the `build` and `serve` modules are already listed, in which the `build` and `serve` commands will be implemented by extending `commis.Command`. We will discuss the `ConsoleProgram` and `Command` interfaces in detail.

The `foo-app.py` should be incredibly simple, even though it is the main entry point to the application. In fact, all it should do is import the console utility from `foo.console.app` and execute it, _that's it_. It will pretty much look as follows:

```python
#!/usr/bin/env python

from foo.console.app import FooApp

if __name__ == '__main__':
    app = FooApp.load()
    app.execute()
```

The shebang (`#!/usr/bin/env python`) ensures that this simple program will execute with Python. Give it executable permissions as follows:

```bash
$ chmod +x foo-app.py
```

This script is the part of your Python project that will eventually get installed into the `$PATH` of the user. Using `setuptools` (`pip`) for packaging, you would simply list `foo-app.py` in the `scripts` keyword argument of the `setup` function as follows:

```python
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='foo',
        version='1.0',
        py_modules=['foo'],
        scripts=['foo-app.py']
    )
```

For more details on Python code organization see [&ldquo;Basic Python Project Files&rdquo;]({% post_url 2016-01-09-project-start %}). For more details on packaging and the `setup.py` file see [&ldquo;Packaging Python Libraries with PyPI&rdquo;]({% post_url 2016-01-20-packaging-with-pypi %}).

## Creating a Console Utility

The Commis library utilizes a class-based interface for defining console utilities and commands. The primary usage is to subclass (extend) both the `ConsoleProgram` and the `Command` class for your purposes, however this is not required. In fact, given two commands, you could easily build a console utility as follows:

```python
#!/usr/bin/env python

from commis import ConsoleProgram
from foo.console.commands import BuildCommand, ServeCommand

app = ConsoleProgram(
    description='my foo app',
    epilog='postscript',
    version='1.0'
)
app.register(BuildCommand)
app.register(ServeCommand)
app.execute()
```

The `ConsoleProgram.register` command takes a `Command` subclass, and registers it to the console utility, building the necessary parser and subparser classes that the `argparse` module requires. You cannot add a command to a console utility without calling `register`. While the register method is easy, it does not allow you to manage, extend, or reuse the utility for different purposes. Instead, I recommend extending `ConsoleProgram` and modifying it as follows.

```python
# foo.console.app
# An extended console utility

import foo

from commis import ConsoleProgram
from foo.console.commands import *

COMMANDS = [
    BuildCommand,
    ServeCommand,
]

class FooApp(ConsoleProgram):

    description = "my foo app"
    epilog      = "please submit any issues to the bug tracker"
    version     = foo.__version__

    @classmethod
    def load(klass, commands=COMMANDS):
        utility = klass()
        for command in commands:
            utility.register(command)
        return utility
```

This technique integrates your application with your library in a couple of meaningful ways. First, the importing and inclusion of commands from in your library means that you can easily control and version which commands are part of the utility and which are deprecated. Secondly, the version is tied to the library version, and other constants like the description and epilog are also easily maintained and can be string formatted from other meta information.

## Creating Commands

Now that we have the infrastructure in place, it's time to start creating commands for our application. Adding new commands to the utility is as simple as creating a command class, importing it in `foo.console.app` and adding the command class to the `COMMANDS` list. This technique means you have an easy way to add, edit, and manage commands without affecting other commands. Here is an example serve command:

```python
from commis import Command

# From the Python standard library
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class ServeCommand(Command):

    name = 'serve'
    help = 'a simple web server which serves files from the working directory'
    args = {
        ('-p', '--port'): {
            'type': int,
            'default': 8080,
            'help': 'the port to serve on',
        },
        ('-a', '--addr'): {
            'type': str,
            'default': 'localhost',
            'help': 'the address to serve on'
        }
    }

    def handle(self, args):
        """
        Create the web server
        """
        server = HTTPServer((args.addr, args.port), SimpleHTTPRequestHandler)
        print "Server started on http://{}:{}".format(args.addr, args.port)

        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            return "Server successfully stopped!"
```

The `Command` subclass basically defines how the command is utilized in the console through four primary attributes: `name`, `help`, `args`, and `handle`. The `name` and `help` arguments are used to describe the command and are passed to the `argparse` library. When you do:

```bash
$ foo-app.py {name} --help
```

The `{name}` is the `Command.name` and the description will be what you listed in `Command.help`. The `args` attribute specifies the expected arguments for parsing on the command line. It is a dictionary, whose key is either a string or a tuple, which defines the name of the argument, and whose value is another dictionary representing the keyword arguments that get passed to `argparse.add_argument`. These arguments are added automatically to the parser and subparser during command registration. Specifying commands this way is a clean and easy way of creating `argparse` subparsers!

### Default Options

There are two default options that are included with _every_ command by default: `--traceback` and `--pythonpath`. The `--traceback` argument specifies that if there is an error, then print out the entire stack trace (similar to what you might expect from a Python program with an exception that is not caught). This is useful for debugging, but often not useful for users. For that reason `--traceback` is by default `False`. Instead, the string representation of the error will be printed in red text. In fact, if there is a user related error, it is usually best to raise a `commis.ConsoleError` with a string message for users in particular:

```python
from commis import Command
from commis.exceptions import ConsoleError

class MyCommand(Command):

    name = 'open'
    help = 'opens the bay doors.'

    def handle(self, args):
        raise ConsoleError("I'm sorry, I cannot do that, Dave.")
```        

The `--pythonpath` option allows you to append paths to `sys.path` to include Python code that is not in your site-packages. This is also good for development and for tools that are intended for developers as it helps avoid import errors.

### Reusing Options

The default options above were created through a subclass of `argparse.ArgumentParser` as shown:

```python
import argparse

class DefaultParser(argparse.ArgumentParser):

    TRACEBACK  = {
        'action':  'store_true',
        'default': False,
        'help': 'On error, show the Python traceback',
    }

    PYTHONPATH = {
        'type': str,
        'required': False,
        'metavar': 'PATH',
        'help': 'A directory to add to the Python path',
    }

    def __init__(self, *args, **kwargs):
        ## Create the parser
        kwargs['add_help'] = False
        super(DefaultParser, self).__init__(*args, **kwargs)

        ## Add the defaults
        self.add_default_arguments()

    def add_default_arguments(self):
        self.add_argument('--traceback', **self.TRACEBACK)
        self.add_argument('--pythonpath', **self.PYTHONPATH)
```

If you have options that you are reusing again and again, you can do something similar for your arguments, e.g. `FooParser`, then add them to your commands with the `parents` attribute as follows:

```python
from commis import Command
from commis.command import DefaultParser
from foo.console import FooParser

class BarCommand(Command):

    name = 'bar'
    help = 'an example command'
    parents = [DefaultParser(), FooParser()]
```

This will ensure that you have both the default arguments as well as the foo arguments that are shared. Additionally if you wish to remove `--traceback` and `--pythonpath` then simply set parents to an empty list.

## Conclusion

In this post we have seen how to build a console utility with Commis - a library designed for easy console programs included with much larger libraries. As you can see, Commis is mostly about code organization and reusability. Hopefully this package will allow you to quickly and easily create utilities of your own. I'm always interested in feedback, please feel free to submit pull requests to the Commis GitHub repository!
