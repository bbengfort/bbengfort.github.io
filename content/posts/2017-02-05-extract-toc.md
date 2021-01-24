---
categories: snippets
date: "2017-02-05T09:11:27Z"
title: Extracting a TOC from Markup
---

In today's addition of &ldquo;really simple things that come in handy all the time&rdquo; I present a simple script to extract the table of contents from markdown or asciidoc files:

{{< gist bbengfort 6ab36e0f518fe3e0f92bce6f53bdd80f >}}

So this is pretty simple, just use regular expressions to look for lines that start with one or more `"#"` or `"="` (for markdown and asciidoc, respectively) and print them out with an indent according to their depth (e.g. indent `##` heading 2 one block). Because this script goes from top to bottom, you get a quick view of the document structure without creating a nested data structure under the hood. I've also implemented some simple type detection using common extensions to decide which regex to use.

The result is a quick view of the structure of a markup file, especially when they can get overly large. From the Markdown of one of my [longer blog posts](http://blog.districtdatalabs.com/a-practical-guide-to-anonymizing-datasets-with-python-faker):

```txt
- A Practical Guide to Anonymizing Datasets with Python
    - Anonymizing CSV Data
        - Generating Fake Data
        - Creating A Provider
    - Maintaining Data Quality
        - Domain Distribution
        - Realistic Profiles
        - Fuzzing Fake Names from Duplicates
    - Conclusion
        - Acknowledgments
        - Footnotes
```

And from the first chapter of [Applied Text Analysis with Python](http://shop.oreilly.com/product/0636920052555.do):

```txt
- Language and Computation
        -
        -
    - What is Language?
        - Identifying the Basic Units of Language
        - Formal vs. Natural Languages
            - Formal Languages
            - Natural Languages
    - Language Models
        - Language Features
        - Contextual Features
        - Structural Features
        - The Academic State of the Art
    - Tools for Natural Language Processing
    - Language Aware Data Products
    - Conclusion
```

Ok, so clearly there are some bugs, those two blank `- ` bullet points are a note callout which has the form:

```asciidoc
[NOTE]
====
Insert note text here.
====
```

Therefore misidentifying the first and second `====` as a level 4 heading. I tried a couple of regular expression fixes for this, but couldn't exactly get it. The next step is to add a simple loop to do multiple paths so that I can print out the table of contents for an entire directory (e.g. to get the TOC for the entire book where one chapter == one file).
