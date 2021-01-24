---
categories: snippets
date: "2016-01-18T10:52:00Z"
title: Simple SQL Query Wrapper
---

Programming with databases is a fact of life for any seasoned programmer (read, &ldquo;worth their salt&rdquo;). From embedded databases like SQLite and LevelDB to server databases like PostgreSQL, data management is a fundamental part of any significant project. The first thing I should say here is _skip the ORM and learn SQL_. SQL is such a powerful tool to query and manage a database, and is far more performant thanks to 40 years of research and development.

Ok, now that we've got that out of the way, the question becomes, how do we embed SQL into our programming language of choice? What you'll typically see in tutorials is the direct embedding of strings into the codebase. While this works, and is nice because now your SQL is also versioned, it can also create many security related complications that I won't go into as well as an organizational nightmare. So you've got to wrap your SQL statements somehow.

Unfortunately, there is no standard answer for this because there are a lot of questions including connection management for performance; size and frequency of queries, etc. Each use case has it's own optimization. Therefore, I'd like to look at a simple wrapper for a Query, as shown in the Gist below and discussed after the code.

{{< gist bbengfort db78948df3ef87091aac >}}

As you can see from the example, we have a routine query where we want to get the orders between a particular time range for a customer identified by their email. Presumably this query will be executed many times in the course of our program, so the factory gives us the ability to run many different queries simultaneously.

Basically what this method gets us is the wrapping of a _parameterized query_ &mdash; e.g. a query that uses [PEP 249](https://www.python.org/dev/peps/pep-0249/) string formatting to add arguments on execution. Calls to query's iterator initiate a connection to the database and execute the query, returning the results of _fetch row_. By using the factory method, this technique basically gives us the ability to execute many queries with different parameters over the course of program execution, such that each query has a separate connection, cursor, and error handling.

There are also two techniques involving the `engine` and the `query` that I generally use. The `engine` in this case connects to a particular database. For a SQLite database you have to specify a path on disk, for a PostgreSQL database a url, username, and password. My preference is to use a [database url](https://pypi.python.org/pypi/dj-database-url) but you'll note that the `Query` object is database-agnostic. Although beyond the scope of this post, a simple `Engine` can be created as follows:

```python
import psycopg2

class PostgreSQLEngine(object):

    def __init__(self, database, user, password, host, port):
        self.params = {
            'database': database,
            'user': user,
            'password': password,
            'host': host,
            'port': port,
        }

    def connect(self):
        return psycopg2.connect(**self.params)


def query_factory(sql, **kwargs):
    def factory():
        return Query(sql, PostgreSQLEngine(**kwargs))
    return factory
```

You could then create an engine object that reads configuration details from [Confire](https://github.com/bbengfort/confire), parses a database URL, or selects from SQLite or PostgreSQL depending on which is available.

Also, the Gist uses a query that is embedded as a [`docstring`](https://www.python.org/dev/peps/pep-0257/). I prefer to store my more complex SQL in `.sql` files and load them from disk. (Smaller queries I might have constants stored in a `queries.py` or similar). This changes the factory again:

```python
def query_factory(path, **kwargs):
    engine = PostgreSQLEngine(**kwargs)
    with open(path, 'r') as f:
        sql = f.read().strip()

    def factory():
        return Query(sql, engine)
    return factory
```

Advanced implementation of this particular technique will use:

- Row format classes to return Python objects or `namedtuples`.
- Context managers to ensure the connection to the database gets closed.
- A connection pool as the engine to reuse connection objects.
- Advanced error handling for not found or parameter errors.

We do this so much that we _plan_ to create a package called [ORMBad](https://github.com/tipsybear/ormbad) which will implement engines and a more advanced query pattern. We just have to get around to doing it!
