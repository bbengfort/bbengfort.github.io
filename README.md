# Libelli

[![Publish](https://github.com/bbengfort/bbengfort.github.io/actions/workflows/publish.yml/badge.svg?branch=main)](https://github.com/bbengfort/bbengfort.github.io/actions/workflows/publish.yml)

**My Github Pages repository for bengfort.github.io**

## Workflow

Create a new post as follows:

```
$ hugo new posts/YYYY-MM-DD-title-slug.md
```

This will create a new file in `content/posts` using the `archetypes/posts.md` archetype. The archetype ensures that the title is correctly extracted from the post path name without the date components as well as the slug. You can then open the file and start editing.

To view the rendered version of the site:

```
$ hugo serve -D
```

Note that the `-D` flag builds drafts and enables you to work on posts before they're published.

Images should be added to the `static/images` folder using a path in the form of `YYYY-MM-DD-image-name.png` -- this is a throwback to the old Jekyll site, and I'd prefer to use content bundles, but we haven't quite made that transition yet. Embed images into markdown posts using the standard markdown with a link from the absolute `images` directory, e.g. `/images/YYYY-MM-DD-image-name.png` from the example above.

To deploy, simply push to the main branch and GitHub Actions will deploy the contents of the `public` directory to GitHub pages. For manual deployment, use the `bin/publish.sh` script.

## About

This page is primarily my development journal and really only contains notes and ramblings for me to refer to as I practice programming. Please feel free to read and use anything you find on this site, but note it is not meant for publication or wide public consumption. If you want to find my more formal writing, check out the [Rotational Labs Blog](https://rotational.io/blog/) where I write about Golang, distributed systems, Python, data science, streaming, and more.

### Name Origin

> A libellus (plural libelli) was a document given to a Roman citizen to certify performance of a pagan sacrifice, hence demonstrating loyalty to the authorities of the Roman Empire. They could also mean certificates of indulgence, in which the confessors or martyrs interceded for apostate Christians. &mdash;[Wikipedia](https://en.wikipedia.org/wiki/Libellus)

So these notes certify the performance of my programming, demonstrating my loyalty to Open Source development, as well as a confession of my programming sins.

### Thanks

This site was built with [Hugo](https://gohugo.io/) using the [PaperMod](https://themes.gohugo.io/hugo-papermod/) theme by [
Aditya Telange](https://github.com/adityatelange/). It is hosted on [GitHub](https://github.com/bbengfort/bbengfort.github.io/) and served with [GitHub Pages](https://pages.github.com/). The logo and icon I've used is [Bear](https://thenounproject.com/search/?q=bear&i=836669) by [Gregor Cresnar](https://thenounproject.com/grega.cresnar) from [the Noun Project](https://thenounproject.com/).
