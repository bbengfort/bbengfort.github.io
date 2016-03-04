---
layout: post
title:  "A Graph Approach to Blocking for Entity Resolution"
#date:   
categories: tutorials
---

> This post is an early draft of expanded work that will eventually appear on the [District Data Labs Blog](http://blog.districtdatalabs.com/). Your feedback is welcome, and you can submit your comments on the [draft GitHub issue](https://github.com/bbengfort/bbengfort.github.io/issues/1).

Entity resolution refers to computational techniques that identify, group, or link digital _mentions_ (records) of some object in the real world (an entity). For example, consider a patient, who is an entity in the context of the health care domain. There are many digital mentions or records concerning the patient from billing records, medical charts, diagnostics, images, etc. All of these records refer to a single entity, but usually have different ways of representing the uniqueness of that entity.

So why is this difficult? In database terms, we might assign a single unique key to an entity, and use that as a reference to all records, thereby allowing us to join different mentions through the key. Natural keys in the real world might be email addresses, social security numbers, state documentation ids, etc. However, besides simple data entry errors (a common source of entity resolution difficulties), the fact that a single entity can be represented by so many identifying data points, mean that different databases may use different keys. Moreover, natural keys, like natural language can be flexible and subject to change.

Entity resolution attempts to ensure that all mentions to a single, unique entity are collected together into a single reference. Specifically tasks like deduplication (removing duplicate entries), record linkage (joining two records together), and canonicalization (creating a single, representative record for an entity) rely on computing the _similarity_ of two records and determining if they are a match or not. Another way to look at this problem is that records are identified by features or fields in similarity space, and we must compute their _distance_. The issue is that distance based computations are very expensive, such that making pairwise comparisons is prohibitive for any reasonably sized data set.

In this blog post we will look at a graph-based approach to _blocking_ for entity resolution &mdash; that is the strategic reduction of the number of pairwise comparisons that are required by using the structure of a natural graph. Blocking provides entity resolution with two primary benefits: increasing the performance by reducing the number of computations, and reducing the search space to propose possible duplicates to a user. In particular, this technique will be used to create a new methodology of annotation for clustering tools like [dedupe](https://github.com/datamade/dedupe).

## A Problem Domain

In this post we will look at a dataset of denormalized subject, predicate, object (SPO) triples that describe how people interact with District Data Labs. For example, the triple:

    (Benjamin Bengfort, taught, Introduction to Machine Learning)

Expresses the relationship between an entity labeled &ldquo;Benjamin Bengfort&rdquo; and a workshop, &ldquo;Introduction to Machine Learning&rdquo; &mdash; namely that I taught it. The dataset of triples form a social activity network: e.g. there is a relationship from the instructor and any person that registered for or took the workshop, through the workshop node by their associated triples.

Participation at District Data Labs is tracked by collecting an _activity log_ of these types of SPOs. Just for the sake of terminology, we will say that the activity log maps a person entity (identified by name and email address) to a DDL detail (e.g. workshop, blog post, incubator, newsletter, etc.), via an activity (identified by a description and a date). The entire dataset is represented in CSV form as follows:

```
Email,FullName,Action,Detail,ActionDate,IPAddress
tashina.lakin@erdman.net,Tashina Lakin,Registered for workshop,Intro to Big Data with Hadoop,3/29/2013,
leonie1535@sengerconroy.org,Leonie Runte,Registered for workshop,Intro to Big Data with Hadoop,3/29/2013,
casper@ortiz.com,Anson Casper,Registered for workshop,Intro to Big Data with Hadoop,3/29/2013,
sbode@lubowitz.com,Starling Bode,Registered for workshop,Intro to Big Data with Hadoop,3/29/2013,
farris.lockman@buckridge.org,Farris Lockman,Registered for workshop,Intro to Big Data with Hadoop,4/3/2013,
ivy168@spinkaheaney.com,Ivy Dicki,Registered for workshop,Intro to Big Data with Hadoop,4/3/2013,
cali.gibson@prohaskakub.com,Cali Gibson,Registered for workshop,Intro to Big Data with Hadoop,4/5/2013,
luke@bellweather.com,"BellWeather, Inc.",Registered for workshop,Intro to Big Data with Hadoop,4/10/2013,
```

**Note**: This data set has been anonymized using the [Faker](http://www.joke2k.net/faker/) library to protect our students and instructors' personally identifying information. For more information on how the dataset was anonymized, see [Anonymizing User Profile Data with Faker](http://bbengfort.github.io/programmer/2016/02/25/anonymizing-profile-data.html).

Because this data is merged from a variety of data sources and web forms, it quickly becomes apparent that there is ambiguity in both the person (subject) entities and the detail (object) entities. For example, is &ldquo;"Anthony Armstrong&rdquo; the same as &ldquo;Tony Armstrong&rdquo;? What if they have the same email address? What about two courses labeled &rdquo;Graph Analytics with Python&rdquo; but who have blocks of registrants with action dates a year apart? Worse, what about the following example:

    John Smith <jsmith@example.com>
    John Smith <john.f.smith@moonstar.edu>

This is such a common name, are they the same or different people? Other types of data errors abound; even in the CSV data above, you can see that one person's name is a company: &ldquo;BellWeather, Inc.&rdquo;. In order to make decisions like these, either in an automatic fashion or by proposing pairs of records to a user, we first need some mechanism to expose likely similar matches, and weed out the obvious non-duplicates.

However, if we make pairwise comparisons between every record in the dataset with no other processing, we will be left with $$c$$ comparisons as follows:

$$
c = \frac { n \left(n-1\right) } {2}
$$

For a relatively modest dataset of 1000 records, you're talking about having to make 499,500 pairwise comparisons. Given that similarity comparison is usually an expensive operation involving dynamic programming and other resource computing techniques, this clearly does not scale well. Through blocking techniques and rules, we can reduce the number of pairwise comparisons by eliminating pairs that will never match. For example, if we have a business listing dataset, we might only compare entities that have the same postal code in their street address. In the next section, we'll look at using a graph to to provide structure for blocking.

## Analyzing Structure with Graphs

A graph is a computational and mathematical data structure composed of _nodes_ and _links_ (alternatively _vertices_ and _edges_). Graphs are used to model complex systems and relationships in the real world, for example communications networks, but also can be used generally in a variety of domains to structure data in a meaningful way<sup><small>[1](#gbfer-footnote-1)</small></sup>. The primary exercise of an analyst when it comes to graph is to determine what the edges and vertices are &mdash; once that is done, many different types of analyses and queries can be made on the structure alone without further information.   

Graphs are computed upon by _traversal_, that is by following a path from node to node through their edges, collecting information along the way. The primary reason that graphs make computation simpler, therefore, is that at each step of computation only nodes that are _neighbors_ (connected via an edge) of the current node need to be analyzed. Traversal based computation means that distance is automatically encoded between nodes by the number of hops it takes to reach one to the other. Queries on graphs leverage distance for filtering or for search by looking only at the closest nodes in the graph.

Hopefully it is clear that the graph structure provides important benefits when it comes to understanding and computing upon complex data. In this section we will explore how to construct and analyze our graph in preparation for deduplication and blocking. To do so we will use the Python NetworkX library, which you should install via `pip` as follows:

    $ pip install networkx

NetworkX is a comprehensive graph analytics package that allows you to load and store graphs in standard data formats, generate many types of graphs, analyze graph structure, and visualize them with `matplotlib` or `graphviz`. Note that these tools also must be installed in order to draw the graphs as we will below.

### Constructing a Graph from a CSV

We will construct our graph using the SPO triples already exposed in our dataset. The subject (person) and object (detail) are nodes that are connected by the predicate (action) edge. NetworkX graph classes require nodes to be hashable<sup><small>[2](#gbfer-footnote-2)</small></sup> Python objects.

Outline:

- reading data from CSV
- namedtuples for hashing into a graph
- constructing a graph from triples
- drawing the graph
- computing # of pairwise comparisons
- computing # of edge blocked comparisons
- printing info about the graph
- performing similarity comparisons
- fuzz blocking

Our approach for blocking will be to eliminate pairs for comparison that share a detail node in its neighborhood. The idea is that since most detail objects require a monetary transaction (e.g. registering for a workshop), it is likely that two are different. However, if an two people register for two different workshops, then they might have done so using a different name or email.

## Conclusion

Entity resolution is a critical first step in building quality data products.  Machine learning involves pattern recognition across a set of instances; duplicated instances can cause noise or error in your model. Moreover, in a relational approach to analytics, duplicated instances can create complex or noisy features spaces which are not easily made separable.

This project is part of the District Data Research Labs on Entity Resolution.

### Resources

The repository for this post is at: [bbengfort/logbook-blocking](https://github.com/bbengfort/logbook-blocking). The dataset can be downloaded from: [ddl-activity-anonymized.csv.zip](http://bit.ly/1TK6UXv)

#### Helpful Links

- [Entity Resolution for Big Data](http://www.datacommunitydc.org/blog/2013/08/entity-resolution-for-big-data)
- [A Primer on Entity Resolution](http://www.slideshare.net/BenjaminBengfort/a-primer-on-entity-resolution)

#### Footnotes


<a name="gbfer-footnote-1">1.</a> [On Graph Computing](http://markorodriguez.com/2013/01/09/on-graph-computing/) gives a more complete look at graphs and how to compute with them.

<a name="gbfer-footnote-2">2.</a> [What do you mean by hashable in Python?](http://stackoverflow.com/questions/14535730/what-do-you-mean-by-hashable-in-python) asked on StackOverflow answers the question succinctly: any immutable or user defined object is hashable by default.
