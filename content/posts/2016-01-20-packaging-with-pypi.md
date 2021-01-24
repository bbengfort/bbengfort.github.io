---
categories: programmer
date: "2016-01-20T15:33:06Z"
title: Packaging Python Libraries with PyPI
---

Package deployment is something that is so completely necessary, but such a pain in the butt that I avoid it a little bit. However to reuse code in Python and to do awesome things like `pip install mycode`, you need to package it up and stick it on to PyPI (pronounced /pīˈpēˈī/ according to one site I read, though I still prefer /pīˈpī/). This process should be easy, but it's detail oriented and there are only two good walk throughs (see links below).

> The Python Package Index or **PyPI** is the official third-party software repository for the Python programming language. Python developers intend it to be a comprehensive catalog of all open source Python packages. &mdash; [Wikipedia](https://en.wikipedia.org/wiki/Python_Package_Index)

I've outlined my process for publishing libraries to PyPI in this post. It is mostly for my own future reference, but I am writing an upcoming post about publishing data projects to PyPI on District Data Labs.

## Getting Started

Before you can publish a package to PyPI, you need to make sure that you're doing Python right. Mostly this means to ensure that you've structured your Python package according to the guide: [_How to Develop Quality Python Code_](http://blog.districtdatalabs.com/how-to-develop-quality-python-code). You should also have several files already part of your project, see [_Basic Python Project Files_]({% post_url 2016-01-09-project-start %}) for those.

However, there are some things you probably haven't done yet, so here is my checklist of stuff to take care of:

<ul class="checklist">
<li>There are at least some tests and continuous integration with <a href="https://travis-ci.org">Travis-CI</a></li>
<li>There is documentation and it's hosted at <a href="https://readthedocs.org/">Read the Docs</a></li>
<li>You have a versioning scheme setup (see below) and the development branching model setup on GitHub.</li>
</ul>

### Creating Accounts

You must create accounts on _both_ the [PyPI Test](https://testpypi.python.org/pypi) and [PyPI Live](https://pypi.python.org/pypi) sites in order to upload code. So do that now and log in to your PyPI account. Once you've done that, create a `.pypirc` configuration file with your account information. Mine looks like this:

```ini
[distutils]
index-servers =
    pypi
    pypitest

[pypi]
repository = https://pypi.python.org/pypi
username   = bbengfort
password   = theeaglefliesatmidnight

[pypitest]
repository = https://testpypi.python.org/pypi
username   = bbengfort
password   = shadowofthedawnawaits
```

Make sure this file is in your home directory; whenever you work with pip or a setup.py file, it will use this configuration for interactions with the remote index servers. As a side note, you can also build your own internal index servers using S3 or other tools!

### Final Notes

Ok for the purposes of this post, we're going to assume that we're working on a library called &ldquo;foo&rdquo; and that the directory structure looks like this:

```
$ project
.
├── .gitignore
├── .travis.yml
├── DESCRIPTION.rst
├── LICENSE.txt
├── Makefile
├── MANIFEST.in
├── mkdocs.yml
├── README.md
├── requirements.txt
├── setup.py
├── setup.cfg
├── bin
|   └── app.py
├── docs
|   ├── images
|   |   └── banner.jpg
|   └── index.md
├── fixtures
├── foo
|   ├── __init__.py
|   └── version.py
└── tests
    └── __init__.py
```

Honestly, I hate that these repos grow to such massive sizes, but honestly, this is a _minimal_ setup for a normal Python project. Or at least, a minimal one the way I do it. Needless to say, I'll be discussing many of these files, in particular, `DESCRIPTION.rst`, `MANIFEST.in`, `requirements.txt`, `setup.py`, `setup.cfg`, and `version.py` in this post. Most of the other files are either self explanatory or contained in another post.

## Setup and Meta

The first step is to configure your project with the necessary setup and meta data files. The first and most important of these is the `setup.py` file which will use the other meta files in the project. Basically, I just copy and paste the following file into all my projects and modify as needed. Apparently this is just a thing Python developers do.

{{< gist bbengfort 76d45a80af5494908c95 >}}

So there is a lot going on here, but you can see that the basic meta information is right at the top. I hoped to top load this file so that copy and paste would be as easy as possible. A couple of notes:

1. The license can just be the name of the license like &ldquo;MIT&rdquo; or &ldquo;Apache&rdquo; &mdash; the `LICENSE.txt` file will spell everything out.
2. The GitHub repository is important; particularly because the download url is formed from a tag, v + the version number.
3. The classifiers **must** be selected from [Python Classifiers](https://pypi.python.org/pypi?%3Aaction=list_classifiers).
4. The `get_version` function must be stored in a file called `version.py` such that the `setup.py` script can read the file and `exec` it _without accidentally importing any dependencies_.
5. Unfortunately, [PyPI doesn't display Markdown](https://coderwall.com/p/qawuyq/use-markdown-readme-s-in-python-modules), so for the long description (which is displayed on the PyPI project page) I have created a file called `DESCRIPTION.rst` which is in reStructuredTxt.
6. The setup script uses the `find_packages` function to discover the contained packages (which allows you to easily create packages with multiple top level modules). Therefore you need to tell it which directories _not_ to look in, as specified by `EXCLUDES`.
7. The script, `bin/app.py` will be installed to the `$PATH` of the user installing the program, but is not included as a module.

I probably do need to break down these notes a bit more, but they are for reference here since I tend to speed write these posts. Check back later, maybe I'll have updated them!

### Configuration and Manifest

The `setup.cfg` file allows you to specify other configurations. In my case it looks like this (assuming a Python 2 and 3 compatible package):

```ini
[metadata]
description-file = README.md

[wheel]
universal = 1
```

Basically the metadata tag is an attempt to get the Markdown README into the package, but it doesn't really work (sadly). The manifest lists all the other files that should be included in the package when uploading to PyPI. Mine looks like this:

```
include *.md
include *.txt
include *.yml
include Makefile
recursive-include docs *.md
recursive-include docs *.jpg
recursive-include tests *.py
recursive-include bin *.py
```

### Final Notes on Configuration

I find it really annoying that you have to create an extra description file for PyPI. Everywhere I read says that you should just put a reStructuredTxt file in as your README, but then of course GitHub doesn't work. I prefer GitHub working, so I go with Markdown. You could write a script to do a conversion with Pandoc, but is it really worth the effort? In the future I'll find a way to manage this a bit better.

If you want the files and directories from `MANIFEST.in` to also be installed (e.g. fixtures or data for machine learning or database setup), you will have to set `include_package_data=True` in your `setup()` call.

## Building and Submitting

Basically there are two phases to submitting a project to PyPI: build and upload. During the upload phase you first send to PyPI Test to make sure everything is good, then send to PyPI live.

### Build

First build the package for distribution along with the binary [wheel](http://pythonwheels.com/) distribution:

```bash
$ python setup.py sdist bdist_wheel
```

This will create a `build` directory with the binary distribution, a `foo.egg-info` directory with packaging information, and finally a `dist` directory with two packages, the versioned distribution (`foo-0.1.tar.gz`) and the wheel (`foo-0.1-py2-none-any.whl`). Note that if you're using my `Makefile`, `make clean` will clean up all of this extra stuff, but it should be ignored in your `.gitignore` already.

At this point you can (and should) test both the wheel and the sdist package by creating a virtual environment and attempting to install the package with `pip` directly as follows:

```bash
$ virtualenv venv
...
$ source venv/bin/activate
$ pip install dist/foo-0.1.tar.gz
$ python
>>> import foo
>>> print foo.__version__
0.1
>>> exit()
$ deactivate
$ rm -rf venv
```

### Upload

The first step to submitting your package to an index server is to register it.

```bash
$ python setup.py register -r pypitest
```

The `-r` flag here specifies which index server you wish to use as listed by the `.pypirc` file. We can then upload the package with [twine](https://pypi.python.org/pypi/twine), which is the currently preferred method of uploading due to its security (TLS) and ability to prebuild and test. If you don't have twine setup, simply `pip install` it.

```bash
$ twine upload -r pypitest dist/foo-0.1*
```

Note that you can also sign the package with a GnuPG key with the `-s` option, but we will skip that for now. Once again, we should test our packages with a virtual environment as above, but this time downloading them from PyPI Test directly:

```bash
$ pip install -i https://testpypi.python.org/pypi foo
```

Once this is done and everything is ready to rock, you can repeat the process for uploading to the package to PyPI, simplified here as follows:

```bash
$ python setup.py register
$ twine upload dist/foo-0.1*
```

### Documentation

Did you know that PyPI [hosts documentation](https://pythonhosted.org/)? Well, it does, and even though you're mainly hosting on [Read the Docs](https://readthedocs.org/) which gets built on each push; it's pretty handy to upload those same docs to PyPI.

Assuming you're using [MkDocs](http://www.mkdocs.org/) as recommended then you can upload this documentation as follows:

```bash
$ mkdocs build --clean
$ python setup.py upload_docs --upload-dir=site
```

### Clean Up

You'll probably want to clean up after yourself, which is as simple as `make clean` if you're using my Makefile. If you'd like to do it with bash it's as follows:

```
$ find . -name "*.pyc" -print0 | xargs -0 rm -rf
$ rm -rf htmlcov
$ rm -rf .coverage
$ rm -rf build
$ rm -rf dist
$ rm -rf foo.egg-info
```

Also you should probably remove that `site` folder created by the documentation build.

## Conclusion

Hopefully this post makes your life easier by giving you a simple guide to push new packages to PyPI. I know I shoot fast and loose with some of the stuff, but the post was super long anyway. If you're really looking for awesome integrations, checkout [How to Travis-CI Deploy](http://5minutes.youkidea.com/howto-deploy-python-package-on-pypi-with-github-and-travis.html) for automatic deployment after testing.

### Very Helpful Links

- [Official Documentation](https://wiki.python.org/moin/CheeseShopTutorial#Submitting_Packages_to_the_Package_Index)
- [How to submit a package to PyPI](http://peterdowns.com/posts/first-time-with-pypi.html)
- [Sharing Your Labor of Love: PyPI Quick and Dirty](https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/)
- [Packaging and Distributing Projects](http://python-packaging-user-guide.readthedocs.org/en/latest/distributing/)
