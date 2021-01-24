---
title: "New Hugo Theme"
date: 2021-01-24T17:12:16-05:00
draft: false
categories: observations
showtoc: true
slug: new-hugo-theme
aliases:
    - /observations/2021/01/24/new-hugo-theme.html
---

A facelift for Libelli today! I moved from [Jekyll](https://jekyllrb.com/) to [Hugo](https://gohugo.io/) for static site generation, a move that has been long overdue &mdash; and I'm very happy I've done it. Not only can I take advantage of a new theme with extra functionality ([PaperMod](https://themes.gohugo.io/hugo-papermod/) in this case) but also because Hugo is written in Go, I feel like I have more control over how the site gets generated.

A lot has been said on this topic, if you're thinking about migrating from Jekyll to Hugo, I recommend [Sara Soueidan's blog post](https://www.sarasoueidan.com/blog/jekyll-ghpages-to-hugo-netlify/) &mdash; the notes here are Libelli specific and are listed here more as notes than anything else.

### Reasons for Switching

These are my personal reasons:

1. Jekyll was getting very difficult to work with; I primarily used the `bundle exec` command, but that would fail more times than not, and because of the frequency that I was writing posts - every time I wanted to write a post I had to update a slough of dependencies.
2. Travis-CI was failing - I had some Jekyll CI integration, but it would fail even though my pages would be built ok; it wasn't inspiring a lot of confidence.
3. I wanted to make changes to the site, but it seemed like I had a giant obstacle of having to update jekyll and the theme first and I'm not very good with Ruby &hellip;
4. Jekyll was taking a _long_ time to build - I had 106 posts before I decided to switch and it was crawling.
5. I wanted to use Hugo for other projects that I am working on.

### Considerations

A few key considerations while making the switch:

1. I really like Hugo's content organization system; unfortunately that would break the permalink structure from Jekyll - the solution was [aliases](https://gohugo.io/content-management/urls/#example-aliases) which allowed me to redirect the old post to the new link which I liked better.
2. Along those lines, I really liked [page-bundles](https://gohugo.io/content-management/page-bundles/#readout) for organizing content. It's a bit tricky to switch with where I'm at now, but I'm going to use it in the future I think.
3. I selected PaperMod primarily because of the search and archive functionality -- which will make finding posts on Libelli much easier. I hope to create a theme of my own someday though.
4. Deploying on GitHub pages - moving away from Jekyll means I don't get builds for free. I'm working on using [Travis CI for deployments](https://creaturesurvive.github.io/repo/blog/hugo-on-github-pages-using-travis-ci-for-deployment/) &mdash; we'll see if it works after this post!
5. I had to write a [script](https://github.com/bbengfort/bbengfort.github.io/blob/master/bin/frontmatter.py) to deal with making changes to the frontmatter to fit my new configuration, the `hugo import jekyll` command did seem to do a lot of work, but I still had to modify the `slug` and the `aliases` configurations as well as bring over defaults from my posts archetype.

### Tricky Bits

Unfortunately (or fortunately), `<script>` tags are cleaned by the Hugo `markdownify` where they weren't in Jekyll. This meant that all my `gist` embeddings had to be updated to the following shortcode:

    {{</* gist bbengfort foo */>}}

Rather then writing a script, I went through this with find and replace.

In [_SVG Vertex with a Timer_]({{< ref "/posts/2016-11-04-svg-timer-vertex.md" >}}), however, I had actual Javascript that I wanted rendered. So I created a `layouts/shortcodes/vertex_timer.html` script and embedded it as a short code in the file with:

    {{</* vertex_timer */>}}

Finally, I had to replace all of the images that used the wrong short code format from Jekyll and replace them with absolute references to their location in the `static` folder. Most of this was copy and paste, but I'm worried I missed something, hence the tricky bits!

### Thoughts

It was very straight forward to move over to Hugo from Jekyll particularly because I was switching themes. I'm very much looking forward to using Hugo from here on out!