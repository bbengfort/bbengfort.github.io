---
layout: post
title:  "NLTK Corpus Reader for Extracted Corpus"
date:   2016-04-11 21:03:18 -0400
categories: snippets
---

Yesterday I wrote a blog about [extracting a corpus]({% post_url 2016-04-10-extract-ddl-corpus %}) from a directory containing Markdown, such as for a blog that is deployed with Silvrback or Jekyll. In this post, I'll briefly show how to use the built in `CorpusReader` objects in `nltk` for streaming the data to the segmentation and tokenization preprocessing functions that are built into NLTK for performing analytics.

The dataset that I'll be working with is the [District Data Labs Blog](http://blog.districtdatalabs.com/), in particular the state of the blog as of today. The dataset can be downloaded from the [ddl corpus](http://bit.ly/ddl-blogs-corpus), which also has the code in this post for you to use to perform other analytics.

The `mdec.py` program extracted our corpus in two formats: html and text. It also setup the corpus as follows:

- README describing the corpus (no extension)
- all text files in the same directory with the .txt or .html extension

If this had been a categorized corpus, then we would have created subdirectories for each category in the corpus, and placed the correct files there. This organization has important implications for using the base readers without too much extension. Plus it helps others understand how to set up corpora with ease.

## Reading Corpora

NLTK's `CorpusReader` objects provide a useful interface to streaming, end-to-end reads of a text corpus from multiple files on disk. To construct a corpus you need to pass the path to the directory containing the corpus, as well as a pattern for a regular expression matching the files that belong to the corpus. By default the `CorpusReader` opens everything with UTF-8 encoding and generally provides the following descriptive methods:

- `readme()`: returns the contents of a README file
- `citation()`: returns the contents of a citation.bib file
- `license()`: returns the contents of a LICENSE file

Generally speaking, your corpora should include all of these meta data files in the root directory in order to be considered complete.

There are many types of `CorpusReader` subclasses available in NLTK. The base classes provide readers for syntax corpora (those that are already structured as parses), bracket corpora (already part of speech tagged), and categorized corpora (documents associated with specific files). There are also a host of readers for the specific corpora that come included with NLTK. In general, these readers should provide an API that contain the following methods:

- `paras()`: returns an iterable of paragraphs (a list of lists of sentences)
- `sents()`: returns an iterable of sentences (a list of lists of words)
- `words()`: returns an iterable of words (a list of words)
- `raw()`: simply returns the raw text from the corpus

Most `CorpusReader` classes can be accessed and filtered by a specific file or category or a list of files or categories. There are two primary methods for listing these if available to the corpus:

- `fileids()`: lists the names of the files that are in the corpus
- `categories()`: lists the names of the categories in the corpus

This listing of API methods is by no means comprehensive. However, for most of the text analytics you'll be doing, these methods will do the bulk of the work. I would consider a CorpusReader complete if it contained all of these methods.

## Reading the Text Corpus

The simplest thing to do is read our plaintext corpus, as we have to write no code to do so. Instead we can simply use the `nltk.corpus.PlaintextCorpusReader` directly, instantiating it with the correct path and pattern for our files. For the DDL corpus this looks like something as follows:

```python
from nltk.corpus.reader.plaintext import PlaintextCorpusReader

corpus = PlaintextCorpusReader(CORPUS_TEXT, '.*\.txt')
```

That's it! As long as we path it a correct path to the corpus and a _pattern_ for identifying text files, then we're good to go! Note that the pattern is formatted as a Python regular expression, hence the escaped `.` -- unfortunately NLTK doesn't use `glob` or other patterns for file identification.

We can now print out some information about our corpus using the reader directly:

```python
from nltk import FreqDist

def corpus_info(corpus):
    """
    Prints out information about the status of a corpus.
    """
    fids   = len(corpus.fileids())
    paras  = len(corpus.paras())
    sents  = len(corpus.sents())
    sperp  = sum(len(para) for para in corpus.paras()) / float(paras)
    tokens = FreqDist(corpus.words())
    count  = sum(tokens.values())
    vocab  = len(tokens)
    lexdiv = float(count) / float(vocab)

    print((
        "Text corpus contains {} files\n"
        "Composed of {} paragraphs and {} sentences.\n"
        "{:0.3f} sentences per paragraph\n"
        "Word count of {} with a vocabulary of {}\n"
        "lexical diversity is {:0.3f}"
    ).format(
        fids, paras, sents, sperp, count, vocab, lexdiv
    ))
```

And the result is:

```text
Text corpus contains 17 files
Composed of 1367 paragraphs and 2817 sentences.
2.061 sentences per paragraph
Word count of 57762 with a vocabulary of 5602
lexical diversity is 10.311
```

Pretty simple!

## Reading the HTML Corpus

The `PlaintextCorpusReader` determined paragraphs as those separated by newlines, something that is not guaranteed for all corpora. HTML documents provide a bit more structure for us to parse, but there is no built in HTML corpus reader, unfortunately. Let's take a look at how to extend our corpus reader to read HTML:

```python
import bs4

class HTMLCorpusReader(PlaintextCorpusReader):

    tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'p', 'li'
    ]

    def _read_word_block(self, stream):
        soup  = bs4.BeautifulSoup(stream, 'lxml')
        return self._word_tokenizer.tokenize(soup.get_text())

    def _read_para_block(self, stream):
        """
        The stream is a single block (file) to extract paragraphs from.
        Method must return list(list(list(str))) of paragraphs, sentences,
        and words, so all tokenizers must be used here.
        """
        soup  = bs4.BeautifulSoup(stream, 'lxml')
        paras = []

        for para in soup.find_all(self.tags):
            paras.append([
                self._word_tokenizer.tokenize(sent)
                for sent in self._sent_tokenizer.tokenize(para.text)
            ])

        return paras
```

The `PlaintextCorpusReader` accepts as additional input a `word_tokenizer`, a `sent_tokenizer`, and a `para_block`: functions that deal with tokenizing the text into various chunks. By default these are the `wordpunct_tokenzie`, `sent_tokenize`, and blank line blocks reader, respectively.

In order to add different functionality, you can either pass a callable into the constructor, or you can override some internal methods. Note that you _should not override the `paras`, `sents`, or `words` methods_ -- these methods handle the streaming. Instead you should override the following protected methods:

- `_read_word_block`: tokenizes 20 lines at a time from the stream.
- `_read_sent_block`: passes the file paragraph at a time into the segmenter.
- `_read_para_block`: deals with a file at a time from the stream.

Although protected, you can see how easy it is to get access to the block stream and override it. Here we simply look for a variety of tags to call "paragraphs" by using `BeautifulSoup`, then correctly return the segmented and tokenized text. Our word block tokenizer simply does an HTML strip tags.
