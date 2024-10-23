#!/usr/bin/env python3

import os

REPO = os.path.dirname(__file__)
BASE = os.path.join(REPO, "..", "content", "posts")


talks = [
    {
        "title": "DIY Consensus: Crafting Your Own Distributed Code (with Benjamin Bengfort)",
        "description": "How do distributed systems work? If you've got a database spread over three servers, how do they elect a leader? How does that change when we spread those machines out across data centers, situated around the globe? Do we even need to understand how it works, or can we relegate those problems to an off the shelf tool like Zookeeper? Joining me this week is Distributed Systems Doctor—Benjamin Bengfort—for a deep dive into consensus algorithms. We start off by discussing how much of \"the clustering problem\" is your problem, and how much can be handled by a library. We go through many of the constraints and tradeoffs that you need to understand either way. And we eventually reach Benjamin's surprising message - maybe the time is ripe to roll your own. Should we be writing our own bespoke Raft implementations? And if so, how hard would that be? What guidance can he offer us?  Somewhere in the recording of this episode, I decided I want to sit down and try to implement a leader election protocol. Maybe you will too. And if not, you'll at least have a better appreciation for what it takes. Distributed systems used to be rocket science, but they're becoming deployment as usual. This episode should help us all to keep up!",
        "youtube": "Ij_PBvocf5c",
        "date": "2023-08-30",
        "link": "https://pod.link/developer-voices/episode/938292a4e4b2c1ca82a66d4674dd8d97",
    },
    {
        "title": "Visual Diagnostics for More Effective Machine Learning",
        "description": "Modeling is often treated as a search activity: find some combination of features, algorithm, and hyperparameters that yields the best score after cross-validation. In this talk, we will explore how to steer the model selection process with visual diagnostics and the Yellowbrick library, leading to more effective and more interpretable results and faster experimental workflows.",
        "youtube": "2kZ38ysHDzM",
        "date": "2019-01-10",
        "slideshare": "127690054",
        "link": "https://pydata.org/miami2019/schedule/presentation/8/",
    },
    {
        "title": "Visual Pipelines for Text Analysis",
        "description": "Employing machine learning in practice is half search, half expertise, and half blind luck. In this talk we will explore how to make the luck half less blind by using visual pipelines to steer model selection from raw input to operational prediction. We will look specifically at extending transformer pipelines with visualizers for sentiment analysis and topic modeling text corpora.",
        "youtube": "",
        "date": "2017-06-24",
        "link": "http://data-intelligence.ai/presentations/13",
    },
    {
        "title": "Data Product Architectures: O'Reilly Webinar",
        "description": "Data products derive their value from data and generate new data in return. As a result, machine-learning techniques must be applied to their architecture and development. Machine learning fits models to make predictions on unknown inputs and must be generalizable and adaptable. As such, fitted models cannot exist in isolation; they must be operationalized and user facing so that applications can benefit from the new data, respond to it, and feed it back into the data product.\n\nData product architectures are, in effect, life-cycles. Understanding the data product life-cycle enables architects to develop robust, failure-free workflows and applications. Benjamin Bengfort discusses the data product life-cycle and outlines the Lambda Architecture, demonstrating how to engage a model build, evaluation, and selection phase with an operation and interaction phase. Benjamin then explores wrapping a central computational store for speed and querying and covers monitoring, management, and data exploration for hypothesis-driven development. From web applications to big data appliances, this architecture serves as a blueprint for handling data services of all sizes.",
        "youtube": "",
        "date": "2016-12-07",
        "link": "http://www.oreilly.com/pub/e/3800",
    },
    {
        "title": "Dynamics in Graph Analysis Adding Time as a Structure for Visual and Statistical Insight",
        "description": "Network analyses are powerful methods for both visual analytics and machine learning but can suffer as their complexity increases. By embedding time as a structural element rather than a property, we will explore how time series and interactive analysis can be improved on Graph structures. Primarily we will look at decomposition in NLP-extracted concept graphs using NetworkX and Graph Tool.\n\nModeling data as networks of relationships between entities can be a powerful method for both visual analytics and machine learning; people are very good at distinguishing patterns from interconnected structures, and machine learning methods get a performance improvement when applied to graph data structures. However, as these structures become more complex or embed more information over time, both visual and algorithmic methods get messy; visual analyses suffer from the \"hairball\" effect, and graph algorithms require either more traversal or increased computation at each vertex. A growing area to reduce this complexity and optimize analytics is the use of interactive and subgraph techniques that model how graph structures change over time.\n\nIn this talk, I demonstrate two practical techniques for embedding time into graphs, not as computational properties, but rather as structural elements. The first technique is to add time as a node to the graph, which allows the graph to remain static and complete, but minimizes traversals and allows filtering. The second is to represent a single graph as multiple subgraphs where each is a snapshot at a particular time. This allows us to use time series analytics on our graphs, but perhaps more importantly, to use animation or interactive methodologies to visually explore those changes and provide meaningful dynamics.",
        "youtube": "QhMZ1PmlJn4",
        "date": "2016-10-24",
        "link": "http://pydata.org/dc2016/schedule/presentation/36/",
        "slideshare": "66065281",
    },
    {
        "title": "Interview - Ben Bengfort of District Data Labs",
        "description": "We talk to Benjamin Bengfort about his Data Day Seattle talks, District Data Labs, and Ben's popular O'Reilly books.",
        "youtube": "ZiY5tjgg7lU",
        "date": "2016-07-28",
        "link": "",
    },
    {
        "title": "Visualizing the Model Selection Process",
        "description": "Machine learning is the hacker art of describing the features of instances that we want to make predictions about, then fitting the data that describes those instances to a model form. Applied machine learning has come a long way from it's beginnings in academia, and with tools like Scikit-Learn, it's easier than ever to generate operational models for a wide variety of applications. Thanks to the ease and variety of the tools in Scikit-Learn, the primary job of the data scientist is _model selection_. Model selection involves performing feature engineering, hyperparameter tuning, and algorithm selection. These dimensions of machine learning often lead computer scientists towards automatic model selection via optimization (maximization) of a model's evaluation metric. However, the search space is large, and grid search approaches to machine learning can easily lead to failure and frustration. Human intuition is still essential to machine learning, and visual analysis in concert with automatic methods can allow data scientists to steer model selection towards better fitted models, faster. In this talk, we will discuss interactive visual methods for better understanding, steering, and tuning machine learning models.",
        "youtube": "",
        "date": "2016-07-23",
        "link": "",
        "slideshare": "64311820",
    },
    {
        "title": "Data Product Architectures: Seattle Data Day",
        "description": "Data products derive their value from data and generate new data in return; as a result, machine learning techniques must be applied to their architecture and their development. Machine learning fits models to make predictions on unknown inputs and must be _generalizable_ and _adaptable_. As such, fitted models cannot exist in isolation; they must be operationalized and user facing so that applications can benefit from the new data, respond to it, and feed it back in to the data product. Data product architectures are therefore _life cycles_ and understanding the data product life cycle will enable architects to develop robust, failure free workflows and applications. In this talk we will discuss the data product life cycle, explore how to engage a model build, evaluation, and selection phase with an operation and interaction phase. Following the lambda architecture, we will investigate wrapping a central computational store for speed and querying, as well as incorporating a discussion of monitoring, management, and data exploration for hypothesis driven development. From web applications to big data appliances; this architecture serves as a blueprint for handling data services of all sizes!",
        "youtube": "",
        "date": "2016-07-21",
        "link": "",
        "slideshare": "64265501",
    },
    {
        "title": "Natural Language Processing with NLTK and Gensim",
        "description": "Natural Language Processing (NLP) is often taught at the academic level from the perspective of computational linguists. However, as data scientists, we have a richer view of the natural language world - unstructured data that by its very nature has latent information that is important to humans. NLP practitioners have benefited from machine learning techniques to unlock meaning from large corpora, and in this class we’ll explore how to do that particularly with Python, Gensim, and the Natural Language Toolkit (NLTK).\n\nNLTK is an excellent library for machine-learning based NLP, written in Python by experts from both academia and industry. Python allows you to create rich data applications rapidly, iterating on hypotheses. The combination of Python + NLTK means that you can easily add language-aware data products to your larger analytical workflows and applications.\n\nIn this tutorial we will begin by exploring NLTK from the view of the corpora that it already comes with, and in this way we will get a feel for the various features and functionality that NLTK has. However, most NLP practitioners want to work on their own corpora, therefore during the second half of the tutorial we will focus on building a language aware data product from a specific corpus - a topic identification and document clustering algorithm from a web crawl of blog sites. The clustering algorithm will use a simple Lesk K-Means clustering to start, and then will improve with an LDA analysis using the Gensim library.",
        "youtube": "itKNpCPHq3I",
        "date": "2016-05-30",
        "link": "https://us.pycon.org/2016/schedule/presentation/1597/",
    },
    {
        "title": "Natural Language Processing and Hadoop",
        "description": "Benjamin Bengfort and Sean Murphy discuss how NLP can be integrated with Hadoop to gain insights in big data.",
        "youtube": "2642kr9-cB0",
        "date": "2013-11-02",
        "link": "http://strataconf.com/stratany2013/public/schedule/detail/30806",
    },
    {
        "title": "Unbound Concepts: Columbia TechBreakfast Dec. 2012",
        "description": "Presentation by the CTO of Unbound Concepts, Benjamin Bengfort, at the Columbia TechBreakfast 2012.",
        "youtube": "N-Bi_MwvZiY",
        "date": "2012-12-12",
        "link": "",
    },
    {
        "title": "Understanding Machine Learning Through Visualizations with Benjamin Bengfort and Rebecca Bilbro - Episode 166",
        "description": "Machine learning models are often inscrutable and it can be difficult to know whether you are making progress. To improve feedback and speed up iteration",
        "youtube": "",
        "date": "2018-06-17",
        "link": "https://www.pythonpodcast.com/yellowbrick-with-bejnamin-bengfort-and-rebecca-bilbro-episode-166/",
    },
]


def main():
    for talk in talks:
        slug = talk["title"].lower().replace(" ", "-")
        path = os.path.join(BASE, f"{talk['date']}-{slug}.md")
        with open(path, 'w') as f:
            f.write("\n".join([
                "---",
                f"title: \"{talk['title']}\"",
                f"slug: \"{slug}\"",
                f"date: \"{talk['date']}T12:00:00-05:00\"",
                "draft: false",
                "categories: presentations",
                "showtoc: false",
                "---\n\n",
            ]))

            if talk["link"]:
                f.write(f"[{talk['title']}]({talk['link']})\n\n")

            if talk["youtube"]:
                f.write("{{< youtube " + talk['youtube'] + " >}}\n\n")

            if 'slideshare' in talk and talk['slideshare']:
                f.write("{{< slideshare id=\"" + talk['slideshare'] + "\" >}}\n\n")

            f.write("### Description\n\n")
            f.write(talk["description"]+"\n\n")


if __name__ == "__main__":
    main()
