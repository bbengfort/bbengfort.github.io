---
categories: snippets
date: "2016-04-10T06:44:28Z"
title: Extracting the DDL Blog Corpus
---

We have some simple text analyses coming up and as an example, I thought it might be nice to use the DDL blog corpus as a data set. There are relatively few DDL blogs, but they all are long with a lot of significant text and discourse. It might be interesting to try to do some lightweight analysis on them.

So, how to extract the corpus? The [DDL blog](http://blog.districtdatalabs.com) is currently hosted on [Silvrback](https://www.silvrback.com/) which is designed for text-forward, distraction-free blogging. As a result, there isn't a lot of cruft on the page. I considered doing a scraper that pulled the web pages down or using the RSS feed to do the data ingestion. After all, I wouldn't have to do a lot of HTML cleaning.

Then I realized -- hey, we have all the Markdown in a repository!

By having everything in one place, as Markdown, I don't have to do a search or a crawl to get all the links. Moreover, I get a bit finer-grained control of what text I want. The question came down to rendering -- do I try to analyze the Markdown, or do I render it into HTML?

In the end, I figured rendering the Markdown to HTML with Python would probably provide the best corpus result. I've created a tool that takes a directory of Markdown files, renders them as HTML or text and then creates the corpus organized directory expected by NLTK. Nicely, this also works with Jekyll! Here is the code:

<script src="https://gist.github.com/bbengfort/d8bc35265861f57c4058ef5b2873b31d.js"></script>

Sorry that was so long, I tried to cut it down a bit, but the `argparse` stuff really does make it quite verbose.  Still the basic methodology is to loop through all the files (recursively going down subdirectories) looking for `*.md` or `*.markdown` files. I then use the Python [Markdown](https://pythonhosted.org/Markdown/) library with the `markdown.extensions.extra` package to render HTML, and to render the text from the HTML, I'm currently using [BeautifulSoup `get_text`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text).

Note also that this tool writes a README with information about the extraction. You can now use the `nltk.PlainTextCorpusReader` to get access to this text! 
