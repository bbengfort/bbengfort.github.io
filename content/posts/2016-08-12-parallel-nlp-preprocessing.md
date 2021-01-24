---
categories: snippets
date: "2016-08-12T22:09:25Z"
title: Parallel NLP Preprocessing
---

A common source of natural language corpora comes from the web, usually in the form of HTML documents. However, in order to actually build models on the natural language, the structured HTML needs to be transformed into units of discourse that can then be used for learning. In particular, we need to strip away extraneous material such as navigation or advertisements, targeting exactly the content we're looking for. Once done, we need to split paragraphs into sentences, sentences into tokens, and assign part-of-speech tags to each token. The preprocessing therefore transforms HTML documents to a list of paragraphs, which are themselves a list of sentences, which are lists of token, tag tuples.

Unfortunately this preprocessing can take a lot of time, particularly for larger corpora. It is therefore efficient to preprocess HTML into these data structures and store them as pickled Python objects, serialized to disk. In order to get the most bang for our buck - we can use multiprocessing to parallelize the preprocessing on each document, increasing the speed of processing due to data parallelism.

In this post, we'll focus on the parallelization aspects, rather than on the preprocessing aspects (you'll have to buy our book for that). In the following code snippet we will look at parallel preprocessing html files in a single directory to pickle files in another directory using the builtin `multiprocessing` library, `nltk` and `beautifulsoup` for the actual work, and `tqdm` to track our progress.

{{< gist bbengfort 8f0e888e222dc65b8742ee02ce59f6e5 >}}

The `preprocess` function takes an input path as well as a directory to write the output to. After reading in the HTML data and creating a parsed `Soup` object using `lxml`, we then extract all `<p>` tags as the paragraphs, apply the `nltk.sent_tokenize` function to each paragraph, then tokenize and tag each sentence. The final data structure is a list of lists of token, tag tuples -- perfect for downstream NLP preprocessing! We then extract the base name of the input path and separate the `.html` extension, adding `.pickle` and creating our output path. From there we can simply open the output file for writing bytes and dump our pickled object to it.

We take advantage of data parallelism (applying the `preprocess` function to each html file) in the `parallelize` function, which takes an input directory and an output directory, as well as the number of tasks to run, which defaults to the number of cores on the machine. The user interface will be a progress bar that displays how many bytes of HTML data have been preprocessed (an alternative is the number of documents processed). First, we list the input directory to get all the paths, then figure out the total number of input bytes using the operating system stat via `os.path.getsize`. We can then instantiate a progress bar with the total and units, and create a callback function that updates the progress bar from the result of the `preprocess` function.

Here is where we get into the parallelism - we create a pool of processes that are ready for work, then use `apply_async` to queue the work (input paths) to the processes. Each process will pop off an input path, perform the preprocessing, then return the file size of the input path it just processed. It will continue to do so as long as there is work. We have to use `apply_async` instead of `map_async` in order to ensure that `on_result` is called after each process completes (thereby updating the progress bar) otherwise the callback wouldn't be called until all work is done.

```
$ python3 parallel.py
100%|██████████████████| 120809/120809 [00:15<00:00, 7237.22Bytes/s]
```

Running this function, you should see a linear speedup in the amount of preprocessing time as the number of processes are increased!
