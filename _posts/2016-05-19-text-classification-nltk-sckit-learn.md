---
layout: post
title:  "Text Classification with NLTK and Scikit-Learn"
date:   2016-05-19 08:06:40 -0400
categories: tutorials
---

> This post is an early draft of expanded work that will eventually appear on the [District Data Labs Blog](http://blog.districtdatalabs.com/). Your feedback is welcome, and you can submit your comments on the [draft GitHub issue](https://github.com/bbengfort/bbengfort.github.io/issues/4).

I've often been asked which is better for text processing, NLTK or Scikit-Learn (and sometimes Gensim). The answer is that I use all three tools on a regular basis, but I often have a problem mixing and matching them or combining them in meaningful ways. In this post, I want to show how I use NLTK for preprocessing and tokenization, but then apply machine learning techniques (e.g. building a linear SVM using stochastic gradient descent) using Scikit-Learn. In a follow on post, I'll talk about vectorizing text with word2vec for machine learning in Scikit-Learn.

As a note, in this post for the sake of speed, I'll be building a text classifier on the movie reviews corpus that comes with NLTK. Here, movie reviews are classified as either positive or negative reviews and this follows a simple sentiment analysis pattern. In the DDL post, I will build a multi-class classifier using the Baleen corpus.

In order to follow along, make sure that you have NLTK and Scikit-Learn installed, and that you have downloaded the NLTK corpus:

```bash
$ pip install nltk scikit-learn
$ python -m nltk.downloader all
```

I will also be using a few helper utilities like a `timeit` decorator and an `identity` function. The complete code for this project can be found here: [sentiment.py](https://gist.github.com/bbengfort/044682e76def583a12e6c09209c664a1). Note that I will also omit imports for the sake of brevity, so please review the complete code if trying to execute the snippets on this tutorial.

## Pipelines

The heart of building machine learning tools with Scikit-Learn is the `Pipeline`. Scikit-Learn exposes a standard API for machine learning that has two primary interfaces: `Transformer` and `Estimator`. Both transformers and estimators expose a `fit` method for adapting internal parameters based on data. Transformers then expose a `transform` method to perform feature extraction or modify the data for machine learning, and estimators expose a `predict` method to generate new data from feature vectors.

Pipelines allow developers to combine a sequential DAG of transformers with an estimator, to ensure that the feature extraction process is associated with the predictive process. This is especially important for text, where raw data is usually in the form of documents on disk or a list of strings. While Sckit-Learn does provide some text based feature extraction mechanisms, actually NLTK is far better suited for this type of text processing. As a result, most of my text processing pipelines have something like this at its core:

[![NLTK Scikit-Learn Text Pipeline]({{ site.base_url }}/assets/images/2016-05-19-nltk-sklearn-text-pipeline.png)]({{ site.base_url }}/assets/images/2016-05-19-nltk-sklearn-text-pipeline.png)

The `CorpusReader` reads files one at a time off a structured corpus (usually zipped) on disk and acts as the source of the data (I also usually include special methods to make sure that I can also get a vector of targets as well). The tokenizer splits raw text into sentences, words and punctuation, then tags their part of speech and lemmatizes them using the WordNet lexicon. The vectorizer encodes the tokens in the document as a feature vector, for example as a TF-IDF vector. Finally the classifier is fit to the documents and their labels, pickled to disk and used to make predictions in the future.

## Preprocessing

In order to limit the number of features, as well as to provide a high quality representation of the text, I use NLTK's advanced text processing mechanisms including the Punkt segmenter and tokenizer, the Brill tagger, and lemmatization using the WordNet lexicon. This not only reduces the vocabulary (and therefore the size of the feature vectors), it also combines redundant features into a single token (e.g. `bunny`, `bunnies`, `Bunny`, `bunny!`, and `_bunny_` all become one feature: `bunny`).

In order to add this type of preprocessing to Scikit-Learn, we must create a Transformer object as follows:

```python
import string

from nltk.corpus import stopwords as sw
from nltk.corpus import wordnet as wn
from nltk import wordpunct_tokenize
from nltk import WordNetLemmatizer
from nltk import sent_tokenize
from nltk import pos_tag

from sklearn.base import BaseEstimator, TransformerMixin


class NLTKPreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, stopwords=None, punct=None,
                 lower=True, strip=True):
        self.lower      = lower
        self.strip      = strip
        self.stopwords  = stopwords or set(sw.words('english'))
        self.punct      = punct or set(string.punctuation)
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y=None):
        return self

    def inverse_transform(self, X):
        return [" ".join(doc) for doc in X]

    def transform(self, X):
        return [
            list(self.tokenize(doc)) for doc in X
        ]

    def tokenize(self, document):
        # Break the document into sentences
        for sent in sent_tokenize(document):
            # Break the sentence into part of speech tagged tokens
            for token, tag in pos_tag(wordpunct_tokenize(sent)):
                # Apply preprocessing to the token
                token = token.lower() if self.lower else token
                token = token.strip() if self.strip else token
                token = token.strip('_') if self.strip else token
                token = token.strip('*') if self.strip else token

                # If stopword, ignore token and continue
                if token in self.stopwords:
                    continue

                # If punctuation, ignore token and continue
                if all(char in self.punct for char in token):
                    continue

                # Lemmatize the token and yield
                lemma = self.lemmatize(token, tag)
                yield lemma

    def lemmatize(self, token, tag):
        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ
        }.get(tag[0], wn.NOUN)

        return self.lemmatizer.lemmatize(token, tag)
```

This is a big chunk of code, so we'll go through it method by method. First when this transformer is initialized, it loads a variety of corpora and models for use in tokenization. By default the set of english stopwords from NLTK is used, and the `WordNetLemmatizer` looks up data from the WordNet lexicon. Note that this takes a noticeable amount of time, and should only be done on instantiation of the transformer.

Next we have the `Transformer` interface methods: `fit`, `inverse_transform`, and `transform`. The first two are simply pass throughs since there is nothing to fit on this class, nor any ability to do `inverse_transform` &mdash; how would you take a lower case lemmatized, unordered tokens and come up with the original text? The best we can do is simply join the tokens with a space. The `transform` method takes a list of documents (given as the variable, X) and returns a new list of tokenized documents, where each document is transformed into list of ordered tokens.

The tokenize method breaks raw strings into sentences, then breaks those sentences into words and punctuation, and applies a part of speech tag. The token is then normalized: made lower case, then stripped of whitespace and other types of punctuation that may be appended. If the token is a stopword or if every character is punctuation, the token is ignored. If it is not ignored, the part of speech is used to lemmatize the token, which is then yielded.

Lemmatization is the process of looking up a single word form from the variety of morphologic affixes that can be applied to indicate tense, plurality, gender, etc. First we need to identify the WordNet tag form based on the Penn Treebank tag, which is returned from NLTK's standard `pos_tag` function. We simply look to see if the Penn tag starts with 'N', 'V', 'R', or 'J' and can correctly identify if its a noun, verb, adverb, or adjective. We then use the new tag to look up the lemma in the lexicon.

## Build and Evaluate

The next stage is to create the pipeline, train a classifier, then to evaluate it. Here I present a very simple version of build and evaluate where:

1. The model is split into a training and testing set by shuffling the data
2. The model is trained on the training set, and evaluated on testing.
3. A new model is then fit on all of the data and saved to disk.

Elsewhere we can discuss evaluation techniques like K-part cross validation, grid search for hyperparameter tuning, or visual diagnostics for machine learning. My simple method is as follows:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report as clsr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split as tts

@timeit
def build_and_evaluate(X, y,
    classifier=SGDClassifier, outpath=None, verbose=True):

    @timeit
    def build(classifier, X, y=None):
        """
        Inner build function that builds a single model.
        """
        if isinstance(classifier, type):
            classifier = classifier()

        model = Pipeline([
            ('preprocessor', NLTKPreprocessor()),
            ('vectorizer', TfidfVectorizer(
                tokenizer=identity, preprocessor=None, lowercase=False
            )),
            ('classifier', classifier),
        ])

        model.fit(X, y)
        return model

    # Label encode the targets
    labels = LabelEncoder()
    y = labels.fit_transform(y)

    # Begin evaluation
    if verbose: print("Building for evaluation")
    X_train, X_test, y_train, y_test = tts(X, y, test_size=0.2)
    model, secs = build(classifier, X_train, y_train)

    if verbose:
        print("Evaluation model fit in {:0.3f} seconds".format(secs))
        print("Classification Report:\n")

    y_pred = model.predict(X_test)
    print(clsr(y_test, y_pred, target_names=labels.classes_))

    if verbose:
        print("Building complete model and saving ...")
    model, secs = build(classifier, X, y)
    model.labels_ = labels

    if verbose:
        print("Complete model fit in {:0.3f} seconds".format(secs))

    if outpath:
        with open(outpath, 'wb') as f:
            pickle.dump(model, f)

        print("Model written out to {}".format(outpath))

    return model
```

This is a fairly procedural method of going about things. There is an inner function, `build` that takes a classifier class or instance (if given a class, it instantiates the classifier with the defaults) and creates the pipeline with that classifier and fits it. Note that when using the `TfidfVectorizer` you must make sure that its default preprocessor, normalizer, and tokenizer are all turned off using the identity function and passing `None` to the other parameters.

The function times the build process, evaluates it via the classification report that reports precision, recall, and F1. Then builds a new model on the complete dataset and writes it out to disk. In order to build the model, run the following code:

```python
from nltk.corpus import movie_reviews as reviews

X = [reviews.raw(fileid) for fileid in reviews.fileids()]
y = [reviews.categories(fileid)[0] for fileid in reviews.fileids()]

model = build_and_evaluate(X,y, outpath=PATH)
```

The output is as follows:

```text
Building for evaluation
Evaluation model fit in 100.777 seconds
Classification Report:

             precision    recall  f1-score   support

        neg       0.84      0.84      0.84       193
        pos       0.85      0.85      0.85       207

avg / total       0.84      0.84      0.84       400

Building complete model and saving ...
Complete model fit in 115.402 seconds
Model written out to model.pickle
```

This is certainly not too bad &mdash; but consider how much time it took. For much larger corpora, you'll only want to run this once, and in a time saving way. You could also preprocess your corpora in advance, however if you did so you would not be able to use the Pipeline as given, and would have to create separate feature extraction and modeling steps.

## Most Informative Features

In order to use the model you just built, you would load the pickle from disk and use it's `predict` method on new text as follows:

```python
with open(PATH, 'rb') as f:
    model = pickle.load(f)

yhat = model.predict([
    "This is the worst movie I have ever seen!",
    "The movie was action packed and full of adventure!"
])

print(model.named_steps['classifier'].labels_.inverse_transform(yhat))
# ['neg' 'pos']
```

In order to better understand how our linear model makes these decisions, we can use the coefficients for each feature (a word) to determine its weight in terms of positivity (and because 'pos' is 1, this will be a positive number) and negativity (because 'neg' is 0 this will be a negative number). We can also vectorize a piece of text and see how it's features inform the class decision by multiplying it's vector against its weights as follows:

```python
def show_most_informative_features(model, text=None, n=20):
    # Extract the vectorizer and the classifier from the pipeline
    vectorizer = model.named_steps['vectorizer']
    classifier = model.named_steps['classifier']

    # Check to make sure that we can perform this computation
    if not hasattr(classifier, 'coef_'):
        raise TypeError(
            "Cannot compute most informative features on {}.".format(
                classifier.__class__.__name__
            )
        )

    if text is not None:
        # Compute the coefficients for the text
        tvec = model.transform([text]).toarray()
    else:
        # Otherwise simply use the coefficients
        tvec = classifier.coef_

    # Zip the feature names with the coefs and sort
    coefs = sorted(
        zip(tvec[0], vectorizer.get_feature_names()),
        key=itemgetter(0), reverse=True
    )

    # Get the top n and bottom n coef, name pairs
    topn  = zip(coefs[:n], coefs[:-(n+1):-1])

    # Create the output string to return
    output = []

    # If text, add the predicted value to the output.
    if text is not None:
        output.append("\"{}\"".format(text))
        output.append(
            "Classified as: {}".format(model.predict([text]))
        )
        output.append("")

    # Create two columns with most negative and most positive features.
    for (cp, fnp), (cn, fnn) in topn:
        output.append(
            "{:0.4f}{: >15}    {:0.4f}{: >15}".format(
                cp, fnp, cn, fnn
            )
        )

    return "\n".join(output)
```

For the model I trained, this reports the 20 most informative features for both positive and negative coefficients as follows:

```text
3.4326            fun    -6.5962            bad
3.3835          great    -3.2906        suppose
3.0014    performance    -3.2527           plot
2.7226            see    -3.1964        nothing
2.5224          quite    -3.1688        attempt
2.5076         matrix    -3.1104  unfortunately
2.1876           also    -3.0741          waste
2.1336           true    -2.5946           poor
2.1140       terrific    -2.5943         boring
2.1076      different    -2.5043          awful
2.0689            job    -2.4893     ridiculous
2.0450      hilarious    -2.4519      carpenter
2.0088           trek    -2.4446           look
1.9704      memorable    -2.2874         stupid
1.9501           well    -2.2667          guess
1.9267      excellent    -2.1953           even
1.8948      sometimes    -2.1946         anyway
1.8939      perfectly    -2.1719           lame
1.8506       bulworth    -2.1406         reason
1.8453        portray    -2.1098         script
```

This seems to make a lot of sense!

## Conclusion

There are great tools for doing machine learning, topic modeling, and text analysis with Python: Scikit-Learn, Gensim, and NLTK respectively. Unfortunately in order to combine these tools in meaningful ways, you often have to jump through some hoops because they overlap. My approach was to leverage the API model of Scikit-Learn to build Pipelines of transformers that took advantage of other libraries. 

### Helpful Links

- [Using Scikit-Learn Pipelines and FeatureUnions](http://zacstewart.com/2014/08/05/pipelines-of-featureunions-of-pipelines.html)
- [Working with Text Data: Sckit-Learn 0.17](http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html)
