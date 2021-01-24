---
categories: snippets
date: "2016-01-21T10:23:06Z"
title: Freezing Package Requirements
---

I have a minor issue with freezing requirements, and so I put together a very complex solution. One that is documented here. Not 100% sure why this week is all about packaging, but there you go.

First up, what is a [requirement file](https://pip.readthedocs.org/en/stable/user_guide/#requirements-files)? Basically they are a list of items that can be installed with `pip` using the following command:

    $ pip install -r requirements.txt

The file therefore mostly serves as a list of arguments to the [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/) command. The requirements file itself has a very [specific format](https://pip.readthedocs.org/en/stable/reference/pip_install/#requirements-file-format) and can be created by hand, but generally the [`pip freeze`](https://pip.pypa.io/en/stable/reference/pip_freeze/) command is used to dump out the requirements as follows:

    $ pip freeze > requirements.txt

This produces an alphabetically sorted list of requirements and dumps them to your requirements text file. It is particularly useful when you are working in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/#other-notes) as you can track your project specific dependencies. Moreover, your [`setup.py`](https://gist.github.com/bbengfort/76d45a80af5494908c95) file can read the `requirements.txt` and install dependencies via `INSTALL_REQUIRES`.   However, consider the following requirements.txt file from [Confire](https://github.com/bbengfort/confire):

```
## Confire requirements
PyYAML==3.11

## Testing requirements
#coverage==3.7.1
#nose==1.3.3
#coveralls==0.5

## Added by virtualenv
#wsgiref==0.1.2
```

Here you can see that we have only one true dependency for Confire, PyYAML. The issue, however, is that we also have the development testing dependencies (nose, coverage, etc.) and then some weird other dependencies from virtualenv or from pip. We've also added comments and whitespace to make this more readable. We have to comment out the testing requirements, because those shouldn't be installed when you `pip install confire` but they should be listed so contributors know what to expect. Luckily, `pip freeze` has us covered in terms of ordering, comments, and whitespace:

    $ pip freeze -r requirements.txt > requirements-new.txt
    $ mv requirements-new.txt requirements.txt

However because the commented packages are skipped before review, you end up with the following:

```
## Confire requirements
PyYAML==3.11

## Testing requirements
#coverage==3.7.1
#nose==1.3.3
#coveralls==0.5

## Added by virtualenv
#wsgiref==0.1.2
## The following requirements were added by pip --freeze:
coveralls==0.5
coverage==3.7.1
nose==1.3.3
wsgiref==0.1.2
```

Like I said, a minor beef. If you've added or upgraded a package, then you have to manually deal with all the commented dependencies. Therefore I created a script to help me with this issue as follows.

{{< gist bbengfort 597b73f5304528f7bef8 >}}

Basically I've stuck this file into `~/bin/requires` and now I can simply do the following to get my requirements:

    $ requires -o reqs.txt
    $ mv reqs.txt requirements.txt

The script automatically detects the local `requirements.txt` file. This script is far from perfect, and the following things I would like to do:

1. Overwrite the actual freeze method [shown on GitHub](https://github.com/pypa/pip/blob/develop/pip/operations/freeze.py) to tighten things up.
2. Deal with new line parsing, inline comments, and versioning a bit better.
3. Output helpful hints to `sys.stderr` as `pip freeze` does.

But for me, this is solving a problem, which is great!
