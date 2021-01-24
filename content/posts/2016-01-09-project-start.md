---
categories: snippets
date: "2016-01-09T14:01:59Z"
title: Basic Python Project Files
---

I don't use project templates like [cookiecutter](https://cookiecutter.readthedocs.org/en/latest/). I'm sure they're fine, but when I start a new project I like to get a cup of coffee, go to my zen place and manually create the workspace. It gets me in the right place to code. Here's the thing, [there is a right way to set up a Python project](http://blog.districtdatalabs.com/how-to-develop-quality-python-code). Plus, I have a particular style for my repositories &mdash; particularly how I use Creative Commons [Flickr](https://www.flickr.com/) photos as the header for my README files.

Here's my primary structure for a project with a primary Python module called &ldquo;foo&rdquo;:

```
$ project
.
├── .gitignore
├── .travis.yml
├── bin
|   └── app.py
├── docs
|   ├── images
|   |   └── banner.jpg
|   └── index.md
├── fixtures
├── foo
|   └── __init__.py
├── LICENSE.txt
├── Makefile
├── mkdocs.yml
├── README.md
├── requirements.txt
├── setup.py
└── tests
    └── __init__.py
```

So, that's actually a lot of files! Maybe I should put myself into copy-and-paste land else my coffee get cold while I'm doing this.

## Make and Dependencies

I use a `Makefile`. I won't apologize. I just like it. I wish there was [something similar](http://stackoverflow.com/questions/1407837/is-there-a-rake-equivalent-in-python) to [rake](http://martinfowler.com/articles/rake.html) for Python. There I said it.

{{< gist bbengfort 17de016d6a51ce487a0f >}}

So this `Makefile` essentially shows how I clean up after myself and run tests, as well as publish to GitHub Pages if I have a subdirectory with HTML for that environment. The requirements are just requirements that I have in basically every single project that I create.

## Versioning

Python modules should be well versioned, especially as I prefer to have good numbering for GitHub releases. Occasionally I will create an actual `version.py` in the root of my module, but more often than not, I just stick it into the `__init__.py` of the module.

{{< gist bbengfort a6d0253982b36bac0049 >}}

To &ldquo;version bump&rdquo; as it were, I simply modify the information in `__version_info__` by updating the release numbers. I also think that someday there is probably also a way to do this automatically or with a version bump script.

## Testing

I like to use a combination of [Travis-CI](https://travis-ci.org/) and [Coveralls](https://coveralls.io/) to get pretty badges on my `README.md` file. Here are my basic test cases and a .travis.yml file.

{{< gist bbengfort 8b58e1ed538a92f44f4e >}}

Note that these files are named for easy location in Gist, not the names of the actual files in the Repository.

## GitHub

My labels in the Github Issues are defined in the blog post: [How we use labels on GitHub Issues at Mediocre Laboratories](https://mediocre.com/forum/topics/how-we-use-labels-on-github-issues-at-mediocre-laboratories). I really like adding both a &ldquo;type&rdquo; and &ldquo;priority&rdquo; to every one of my cards. Makes issue management so much easier.

I also now tend to use both a master and a develop branch, such that my branches are setup in a typical production/release/development cycle as described in _[A Successful Git Branching Model](http://nvie.com/posts/a-successful-git-branching-model/)_. A typical workflow is as follows:

1. Select a card from the [dev board](https://waffle.io/) - preferably one that is "ready" then move it to "in-progress".

2. Create a branch off of develop called &ldquo;feature-[feature name]&rdquo;, work and commit into that branch.

        ~$ git checkout -b feature-myfeature develop

3. Once you are done working (and everything is tested) merge your feature into develop.

        ~$ git checkout develop
        ~$ git merge --no-ff feature-myfeature
        ~$ git branch -d feature-myfeature
        ~$ git push origin develop

4. Repeat. Releases will be routinely pushed into master via release branches, then deployed to the server.

Pull requests will be reviewed when the Travis-CI tests pass, so including tests with your pull request is ideal!

## README.md

And finally, here is some Markdown that I typically use for the README:

{{< gist bbengfort 778adad3917291e64213 >}}

Ok, that's all the project templates for now!
