---
categories: observations
date: "2016-10-28T13:16:24Z"
title: Computing Reading Speed
---

Ashley and I have been going over the [District Data Labs Blog](http://blog.districtdatalabs.com/) trying to figure out a method to make it more accessible both to readers (who are at various levels) and to encourage writers to contribute. To that end, she's been exploring other blogs to see if we can put multiple forms of content up; long form tutorials (the bulk of what's there) and shorter idea articles, possibly even as short as the posts I put on my dev journal. One interesting suggestion she had was to mark the reading time of each post, something that [ the Longreads Blog](http://bit.ly/2ePtm3z) does. This may help give readers a better sense of the time committment and be able to engage more easily.

So computing the reading time is simple right? Take the number of words in the post divided by the average words per minute reading rate and bam - the number of minutes per post. Also, we're not going to simply split on space, we know better - so we can use NLTK's `word_tokenize` function. Seems like we're good to go, but what's the average words per minute reading rate of the average DDL reader?

After a bit of a search, we first found [a study published by Reading Plus](http://bit.ly/2eMmbqY) that charted the normal reading read in words per minute against high school grade level. Unfortunately, this led to the question, what level is our content at? Further searching found an [LSAT reading speed calculation formula](http://bit.ly/2eMfc0X) by Graeme Blake, moderator of the Reddit LSAT forum. We figured our content is probably as complex as the LSAT, and moreover, he gave speeds for slow, average, high average, fast, and rare LSAT students.

We ran each of these WPM speeds against published articles in the DDL corpus and came up with the following words per minute for each title:

| Post                                                             | LSAT       | Slow       | Average    | Fast       |
|:-----------------------------------------------------------------|:-----------|:-----------|:-----------|:-----------|
| [Announcing the District Data Labs Blog](http://blog.districtdatalabs.com/announcing-the-district-data-labs-blog)           | 26 seconds | 23 seconds | 18 seconds | 15 seconds |
| [How to Transition from Excel to R](http://blog.districtdatalabs.com/intro-to-r-for-microsoft-excel-users)                | 12 minutes | 11 minutes | 9 minutes  | 7 minutes  |
| [What Are the Odds?](http://blog.districtdatalabs.com/intro-to-probability-with-r)                       | 12 minutes | 10 minutes | 8 minutes  | 7 minutes  |
| [How to Develop Quality Python Code](http://blog.districtdatalabs.com/how-to-develop-quality-python-code)               | 28 minutes | 25 minutes | 20 minutes | 17 minutes |
| [Markup for Fast Data Science Publication](http://blog.districtdatalabs.com/markup-for-fast-data-science-publication)          | 16 minutes | 14 minutes | 11 minutes | 9 minutes  |
| [The Age of the Data Product](http://blog.districtdatalabs.com/the-age-of-the-data-product)                       | 27 minutes | 24 minutes | 19 minutes | 16 minutes |
| [A Practical Guide to Anonymizing Datasets with Python & Faker](http://blog.districtdatalabs.com/a-practical-guide-to-anonymizing-datasets-with-python-faker)                              | 19 minutes | 17 minutes | 14 minutes | 11 minutes |
| [Computing a Bayesian Estimate of Star Rating Means](http://blog.districtdatalabs.com/computing-a-bayesian-estimate-of-star-rating-means)                   | 19 minutes | 17 minutes | 14 minutes | 11 minutes |
| [Conditional Probability with R](http://blog.districtdatalabs.com/conditional-probability-with-r)                              | 12 minutes | 11 minutes | 9 minutes  | 7 minutes  |
| [Creating a Hadoop Pseudo-Distributed Environment](http://blog.districtdatalabs.com/creating-a-hadoop-pseudo-distributed-environment)             | 13 minutes | 12 minutes | 10 minutes | 8 minutes  |
| [Getting Started with Spark (in Python)](http://blog.districtdatalabs.com/getting-started-with-spark-in-python)                                  | 32 minutes | 29 minutes | 23 minutes | 19 minutes |
| [Graph Analytics Over Relational Datasets with Python](http://blog.districtdatalabs.com/graph-analytics-over-relational-datasets)                        | 11 minutes | 10 minutes | 8 minutes  | 7 minutes  |
| [An Introduction to Machine Learning with Python](http://blog.districtdatalabs.com/an-introduction-to-machine-learning-with-python)                 | 18 minutes | 16 minutes | 13 minutes | 11 minutes |
| [Modern Methods for Sentiment Analysis](http://blog.districtdatalabs.com/modern-methods-for-sentiment-analysis)                        | 12 minutes | 11 minutes | 9 minutes  | 7 minutes  |
| [Parameter Tuning with Hyperopt](http://blog.districtdatalabs.com/parameter-tuning-with-hyperopt)                               | 12 minutes | 11 minutes | 9 minutes  | 7 minutes  |
| [Simple CSV Data Wrangling with Python](http://blog.districtdatalabs.com/simple-csv-data-wrangling-with-python)                                         | 18 minutes | 16 minutes | 13 minutes | 11 minutes |
| [Time Maps: Visualizing Discrete Events Across Many Timescales](http://blog.districtdatalabs.com/time-maps-visualizing-discrete-events-across-many-timescales) | 10 minutes | 9 minutes  | 7 minutes  | 6 minutes  |

We'd be happy to have any feedback on if these times look correct or not. The code to produce the table follows:

{{< gist bbengfort 1fadc447c45bff18bbde5ff3d59a08ee >}}

Of course this is a straight count of words and does not take into account the number of sections or whether or not there are any code blocks. In the future, I hope to do an HTML version of this that takes into account the number of paragraphs, the density of each paragraph and the length of sentences, as well as the frequency of vocabulary words etc. I'll need to gather feedback for a supervised learning algorithm though to train actual WPM on these features!
