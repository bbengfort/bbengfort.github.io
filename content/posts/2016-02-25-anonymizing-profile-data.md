---
categories: programmer
date: "2016-02-25T12:32:54Z"
title: Anonymizing User Profile Data with Faker
---

> This post is an early draft of expanded work that will eventually appear on the [District Data Labs Blog](http://blog.districtdatalabs.com/). Your feedback is welcome, and you can submit your comments on the [draft GitHub issue](https://github.com/bbengfort/bbengfort.github.io/issues/3).

In order to learn (or teach) data science you need data (surprise!). The best libraries often come with a toy dataset to show examples and how the code works. However, nothing can replace an actual, non-trivial dataset for a tutorial or lesson because it provides for deep and meaningful further exploration. Non-trivial datasets can provide surprise and intuition in a way that toy datasets just cannot. Unfortunately, non-trivial datasets can be hard to find for a few reasons, but one common reason is that the dataset contains personally identifying information (PII).

A possible solution to dealing with PII is to _anonymize_<sup><small>[1](#apd-footnote-1)</small></sup> the data set by replacing information that can identify a real individual with information about a fake (but similarly behaving) fake individual. Unfortunately this is not as easy at it sounds at a glance. A simple mapping of real data to randomized data is not enough because anonymization needs to preserve the semantics of the dataset in order to be used as a stand in for analytical purposes. As a result, issues related to _entity resolution_<sup><small>[2](#apd-footnote-2)</small></sup> like managing duplicates or producing linkable results come into play.

The good news is that we can take a cue from the database community, who routinely _generate_ data sets in order to evaluate the performance of a database system. This community, especially in a web or test driven development context, has a lot of tools for generating very realistic data for a variety of information types. For this post, I'll explore using the [Faker](https://github.com/joke2k/faker) library to generate a realistic, anonymized dataset that can be utilized for downstream analysis.

The goal can therefore be summarized as follows: given a target dataset (let's say for simplicity, a CSV file with multiple columns), produce a new dataset such that for each row in the target, the anonymized dataset does not contain any personally identifying information. The anonymized dataset should have the same amount of data, as well as maintain its value for analysis.

## Anonymizing CSV Data

In this example we're going to do something very simple, we're going to anonymize only two fields: full name and email. Sounds easy, right? The issue is that we want to preserve the semantic relationships and patterns in our target dataset so that we can hand it off to be analyzed or mined for interesting patterns. What happens if there are multiple rows per user? Since CSV data is naturally denormalized (e.g. contains redundant data like rows with repeated full names and emails) we will need to maintain a mapping of profile information.

**Note**: Since we're going to be using Python 2.7 in this example, you'll need to install the `unicodecsv` module with `pip`. Additionally you'll need the Faker library:

    $ pip install fake-factory unicodecsv

The following example shows a simple `anonymize_rows` function that maintains this mapping and also shows how to generate data with Faker. We'll also go a step further and read the data from a source CSV file and write the anonymized data to a target CSV file. The end result is that the file should be very similar in terms of length, row order, and fields, the only difference being that names and emails have been replaced with fake names and emails.

```python
import unicodecsv as csv
from faker import Factory
from collections import defaultdict

def anonymize_rows(rows):
    """
    Rows is an iterable of dictionaries that contain a name and
    email field that need to be anonymized.
    """
    # Load the faker and its providers
    faker  = Factory.create()

    # Create mappings of names & emails to faked names & emails.
    names  = defaultdict(faker.name)
    emails = defaultdict(faker.email)

    # Iterate over the rows and yield anonymized rows.
    for row in rows:
        # Replace the name and email fields with faked fields.
        row['name']  = names[row['name']]
        row['email'] = emails[row['email']]

        # Yield the row back to the caller
        yield row


def anonymize(source, target):
    """
    source is a path to a CSV file containing data to anonymize.
    target is a path to write the anonymized CSV data to.
    """
    with open(source, 'rU') as f:
        with open(target, 'w') as o:
            # Use the DictReader to easily extract fields
            reader = csv.DictReader(f)
            writer = csv.DictWriter(o, reader.fieldnames)

            # Read and anonymize data, writing to target file.
            for row in anonymize_rows(reader):
                writer.writerow(row)

```

The entry point for this code is the `anonymize` function itself. It takes as input the path to two files: the `source`, where the target data is held in CSV form, and `target` a path to write out the anonymized data to. Both of these paths are opened for reading and writing respectively, then the `unicodecsv` module is used to read and parse each row, transforming them into Python dictionaries. Those dictionaries are passed into the `anonymize_rows` function, which transforms and `yields` each row to be written by the CSV writer to disk.

The `anonymize_rows` function takes any iterable of dictionaries which contain `name` and `email` keys. It loads the fake factory using `Factory.create` - a class function that loads various providers with methods that generate fake data (more on this later). We then create two `defaultdict` to map names to fake names and emails to fake emails.

The Python `collections` module provides the `defaultdict` which is similar to a regular `dict` except that if the key does not exist in the dictionary, a default value is supplied by the callable passed in at instantiation. For example, `d = defaultdict(int)` would provide a default value of 0 for every key not already in the dictionary. Therefore when we use `defaultdict(faker.name)` we're saying that for every key not in the dictionary, create a fake name (and similar for email). This allows us to generate a mapping of real data to fake data, and make sure that the real value always maps to the same fake value.

From there we simply iterate through all the rows, replacing data as necessary. If our target CSV file looked like this (imagine clickstream data from an email marketing campaign):

```
name,email,value,time,ipaddr
James Hinglee,jhinglee@gmail.com,a,1446288248,202.12.32.123
Nancy Smithfield,unicorns4life@yahoo.com,b,1446288250,67.212.123.201
J. Hinglee,jhinglee@gmail.com,b,1446288271,202.12.32.123
```

It would be transformed to something as follows:

```
Mr. Sharif Lehner,keion.hilll@gmail.com,a,1446288248,202.12.32.123
Webster Kulas,nienow.finnegan@gmail.com,b,1446288250,67.212.123.201
Maceo Turner MD,keion.hilll@gmail.com,b,1446288271,202.12.32.123
```

We now have a new wrangling tool in our toolbox that will allow us to transform CSVs with name and email fields into anonymized datasets! This naturally leads us to the question: what else can we anonymize?

### Generating Fake Data

There are two third party libraries for generating fake data with Python that come up on Google search results: [Faker](https://pypi.python.org/pypi/Faker) by [@deepthawtz](https://github.com/deepthawtz) and [Fake Factory](https://pypi.python.org/pypi/fake-factory) by [@joke2k](https://github.com/joke2k), which is also called &ldquo;Faker&rdquo;. Faker provides anonymization for user profile data, which is completely generated on a per-instance basis. Fake Factory (used in the example above) uses a providers approach to load many different fake data generators in multiple languages. Because Fake Factory has multiple language support, and a wider array of fake data generators, I typically use it over the more intuitive and simple to use Faker library which only does fake user profiles and we'll inspect it in detail for the rest of this post (everywhere except in this paragraph, when I refer to Faker, I'm referring to Fake Factory).

The primary interface that Faker provides is called a `Generator`. Generators are a collection of `Provider` instances which are responsible for formatting random data for a particular domain. Generators also provide a wrapper around the `random` module, and allow you to set the random seed and other operations. While you could theoretically instantiate your own Generator with your own providers, Faker provides a `Factory` to automatically load all the providers on your behalf:

```python
>>> from faker import Factory
>>> fake = Factory.create()
```

If you inspect the `fake` object, you'll see around 158 methods (at the time of this writing) that all generate fake data. Please allow me to highlight a few:

```python
>>> fake.credit_card_number()
u'180029425031151'
```

```python
>>> fake.military_ship()
u'USCGC'
```

```python
>>> (fake.latitude(), fake.longitude())
(Decimal('-39.4682475'), Decimal('50.449170'))
```

```python
>>> fake.hex_color()
u'#559135'
```

```python
>>> fake.pyset(3)
set([u'Et possimus.', u'Blanditiis vero.', u'Ad odio ad qui.', 9855])
```

Importantly, providers can also be localized using a language code; and this is probably the best reason to use the `Factory` object &mdash; to ensure that localized providers, or subsets of providers are loaded correctly. For example, to load the French localization:

```python
>>> fake = Factory.create('fr_FR')
>>> fake.catch_phrase_verb()
u"d'atteindre vos buts"
```

And for fun, some Chinese:

```python
>>> fake = Factory.create('cn_ZH')
>>> print fake.company()
u"快讯科技有限公司"
```

As you can see there are a wide variety of tools and techniques to generate fake data from a variety of domains. The best way to explore all the providers in detail is simply to look at the [providers package on GitHub](https://github.com/joke2k/faker/tree/master/faker/providers).

### Creating A Provider

Although the Faker library has a very comprehensive array of providers, occasionally you need a domain specific fake data generator. In order to add a custom provider, you will need to subclass the `BaseProvider` and expose custom fake methods as class methods using the `@classmethod` decorator. One very easy approach is to create a set of random data you'd like to expose, and simply randomly select it:

```python
from faker.providers import BaseProvider

class OceanProvider(BaseProvider):

    __provider__ = "ocean"
    __lang__     = "en_US"

    oceans = [
        u'Atlantic', u'Pacific', u'Indian', u'Arctic', u'Southern',
    ]

    @classmethod
    def ocean(cls):
        return cls.random_element(cls.oceans)
```

In order to change the likelihood or distribution of which oceans are selected, simply add duplicates to the `oceans` list so that each name has the probability of selection that you'd like. Then add your provider to the `Faker` object:

```python
>>> fake = Factory.create()
>>> fake.add_provider(OceanProvider)
>>> fake.ocean()
u'Indian'
```

In routine data wrangling operations, you may create a package structure with localization similar to how Faker is organized and load things on demand. Don't forget &mdash; if you come up with a generic provider that may be useful to many people, submit it back as a pull request!

## Maintaining Data Quality

Now that we understand the wide variety of fake data we can generate, let's get back to our original example of creating user profile data of just name and email address. First, if you look at the results in the section above, we can make a few observations:

- **Pro**: exact duplicates of name and email are maintained via the mapping.
- **Pro**: our user profiles are now fake data and PII is protected.
- **Con**: the name and the email are weird and don't match.
- **Con**: fuzzy duplicates (e.g. J. Smith vs. John Smith) are blown away.
- **Con**: all the domains are "free email" like Yahoo and Gmail.

Basically we want to improve our user profile to include email addresses that are similar to the names (or a non-name based username), and we want to ensure that the domains are a bit more realistic for work addresses. We also want to include aliases, nicknames, or different versions of the name. Faker does provide a profile provider:

```python
>>> fake.simple_profile()
u'{
  "username": "autumn.weissnat",
  "name": "Jalyn Crona",
  "birthdate": "1981-01-29",
  "sex": "F",
  "address": "Unit 2875 Box 1477\nDPO AE 18742-1954",
  "mail": "zollie.schamberger@hotmail.com"
}'
```

But as you can see, it suffers from the same problem. In this section, we'll explore different techniques that allow us to pass over the data and modify our fake data generation such that it matches the distributions we're seeing in the original data set. In particular we'll deal with the domain, creating more realistic fake profiles, and adding duplicates to our data set with fuzzy matching.

### Domain Distribution

One idea to maintain the distribution of domains is to do a first pass over the data and create a mapping of real domain to fake domain. Moreover, many domains like gmail.com can be whitelisted and mapped directly to itself (we just need a fake username). Additionally, we can also preserve capitalization and spelling via this method, e.g. &ldquo;Gmail.com&rdquo; and &ldquo;GMAIL.com&rdquo; which might be important for data sets that have been entered by hand.

In order to create the domain mapping/whitelist, we'll need to create an object that can load a whitelist from disk, or generate one from our original dataset. I propose the following utility:

```python
import csv
import json

from faker import Factory
from collections import Counter
from collections import MutableMapping

class DomainMapping(MutableMapping):

    @classmethod
    def load(cls, fobj):
        """
        Load the mapping from a JSON file on disk.
        """
        data = json.load(fobj)
        return cls(**data)

    @classmethod
    def generate(cls, emails):
        """
        Pass through a list of emails and count domains to whitelist.
        """
        # Count all the domains in each email address
        counts  = Counter([
            email.split("@")[-1] for email in emails
        ])

        # Create a domain mapping
        domains = cls()

        # Ask the user what domains to whitelist based on frequency
        for idx, (domain, count) in enumerate(counts.most_common())):
            prompt = "{}/{}: Whitelist {} ({} addresses)?".format(
                idx+1, len(counts), domain, count
            )

            print prompt
            ans = raw_input("[y/n/q] > ").lower()

            if ans.startswith('y'):
                # Whitelist the domain
                domains[domain] = domain
            elif ans.startswith('n'):
                # Create a fake domain
                domains[domain]
            elif ans.startswith('q'):
                break
            else:
                continue

        return domains  

    def __init__(self, whitelist=[], mapping={}):
        # Create the domain mapping properties
        self.fake    = Factory.create()
        self.domains = mapping

        # Add the whitelist as a mapping to itself.
        for domain in whitelist:
            self.domains[domain] = domain

    def dump(self, fobj):
        """
        Dump the domain mapping whitelist/mapping to JSON.
        """
        whitelist = []
        mapping   = self.domains.copy()
        for key in mapping.keys():
            if key == mapping[key]:
                whitelist.append(mapping.pop(key))

        json.dump({
            'whitelist': whitelist,
            'mapping': mapping
        }, fobj, indent=2)

    def __getitem__(self, key):
        """
        Get a fake domain for a real domain.
        """
        if key not in self.domains:
            self.domains[key] = self.fake.domain_name()
        return self.domains[key]

    def __setitem__(self, key, val):
        self.domains[key] = val

    def __delitem__(self, key):
        del self.domains[key]

    def __iter__(self):
        for key in self.domains:
            yield key
```

Right so that's quite a lot of code all at once, so let's break it down a bit. First, the class extends `MutableMapping` which is an abstract base class in the `collections` module. The ABC gives us the ability to make this class act just like a `dict` object. All we have to do is provide `__getitem__`, `__setitem__`, `__delitem__`, and `__iter__` methods and all other dictionary methods like `pop`, or `values` work on our behalf. Here, we're just wrapping an inner dictionary called `domains`.

The thing to note about our `__getitem__` method is that it acts very similar to a `defaultdict`, that is if you try to fetch a key that is not in the mapping, then it generates fake data on your behalf. This way, any domains that we don't have in our whitelist or mapping will automatically be anonymized.

Next, we want to be able to `load` and `dump` this data to a JSON file on disk, that way we can maintain our mapping between anonymization runs. The `load` method is fairly straight forward, it just takes an open file-like object and parses it uses the `json` module, and instantiates the domain mapping and returns it. The `dump` method is a bit more complex, it has to break down the whitelist and mapping into separate objects, so that we can easily modify the data on disk if needed. Together, these methods will allow you to load and save your mapping into a JSON file that will look similar to:

```json
{
    "whitelist": [
        "gmail.com",
        "yahoo.com"
    ],
    "mapping": {
        "districtdatalabs.com": "fadel.org",
        "umd.edu": "ferrystanton.org"
    }
}
```

The final method of note is the `generate` method. The generate method allows you to do a first pass through a list of emails, count the frequency of the domains, then propose to the user in order of most frequent domain whether or not to add it to the whitelist. For each domain in the emails, the user is prompted as follows:

```
1/245: Whitelist "gmail.com" (817 addresses)?
[y/n/q] >
```

Note that the prompt includes a progress indicator (this is prompt 1 of 245) as well as a method to quit early. This is especially important for large datasets that have a lot of single domains; if you quit, the domains will still be faked, and the user only sees the most frequent examples for whitelisting. The idea behind this mechanism to read through your CSV once, generate the whitelist, then save it to disk so that you can use it for anonymization on a routine basis. Moreover, you can modify domains in the JSON file to better match any semantics you might have (e.g. include .edu or .gov domains, which are not generated by the internet provider in Faker).

### Realistic Profiles

To create realistic profiles, we'll create a provider that uses the domain map from above and generates fake data for every combination we see in the data set. This provider will also provide opportunities for mapping multiple names and email addresses to a single profile so that we can use the profile for creating fuzzy duplicates in the next section. Here is the code:

```python
class Profile(object):

    def __init__(self, domains):
        self.domains = domains
        self.generator = Factory.create()

    def fuzzy_profile(self, name=None, email=None):
        """
        Return an profile that allows for fuzzy names and emails.
        """
        parts = self.fuzzy_name_parts()
        return {
            "names": {name: self.fuzzy_name(parts, name)},
            "emails": {email: self.fuzzy_email(parts, email)},
        }

    def fuzzy_name_parts(self):
        """
        Returns first, middle, and last name parts
        """
        return (
            self.generator.first_name(),
            self.generator.first_name(),
            self.generator.last_name()
        )

    def fuzzy_name(self, parts, name=None):
        """
        Creates a name that has similar case to the passed in name.
        """
        # Extract the first, initial, and last name from the parts.
        first, middle, last = parts

        # Create the name, with chance of middle or initial included.
        chance = self.generator.random_digit()
        if chance < 2:
            fname = u"{} {}. {}".format(first, middle[0], last)
        elif chance < 4:
            fname = u"{} {} {}".format(first, middle, last)
        else:
            fname = u"{} {}".format(first, last)

        if name is not None:
            # Match the capitalization of the name
            if name.isupper(): return fname.upper()
            if name.islower(): return fname.lower()

        return fname

    def fuzzy_email(self, parts, email=None):
        """
        Creates an email similar to the name and original email.
        """
        # Extract the first, initial, and last name from the parts.
        first, middle, last = parts

        # Use the domain mapping to identify the fake domain.
        if email is not None:
            domain = self.domains[email.split("@")[-1]]
        else:
            domain = self.generator.domain_name()

        # Create the username based on the name parts
        chance = self.generator.random_digit()
        if chance < 2:
            username = u"{}.{}".format(first, last)
        elif chance < 3:
            username = u"{}.{}.{}".format(first, middle[0], last)
        elif chance < 6:
            username = u"{}{}".format(first[0], last)
        elif chance < 8:
            username = last
        else:
            username = u"{}{}".format(
                first, self.generator.random_number()
            )

        # Match the case of the email
        if email is not None:
            if email.islower(): username = username.lower()
            if email.isupper(): username = username.upper()
        else:
            username = username.lower()

        return u"{}@{}".format(username, domain)
```

Again, this is a lot of code, make sure you go through it carefully so you understand what is happening. First off, a profile in this case is the combination of a mapping of names to fake names and emails to fake emails. The key is that the names and emails are related to original data somehow. In this case, the relationship is through case such that "DANIEL WEBSTER" is faked to "JAKOB WILCOTT" instead of to "Jakob Wilcott". Additionally through our domain mapping, we also maintain the relationship of the original email domain to the fake domain mapping, e.g. everyone with the an email domain "@districtdatalabs.com" will be mapped to the same fake domain.

In order to maintain the relationship of names to emails (which is very common), we need to be able to access the name more directly. In this case we have a name parts generator which generates fake first, middle, and last names. We then randomly generate names of the form "first last", "first middle last", or "first i. last" with random chance. Additionally the email can take a variety of forms based on the name parts as well. Now we get slightly more realistic profiles:

```python
>>> fake.fuzzy_profile()
{'names': {None: u'Zaire Ebert'}, 'emails': {None: u'ebert@von.com'}}
```

```python
>>> fake.fuzzy_profile(
...    name='Daniel Webster', email='dictionaryguy@gmail.com')
{'names': {'Daniel Webster': u'Georgia McDermott'},
 'emails': {'dictionaryguy@gmail.com': u'georgia9@gmail.com'}}
```

Importantly this profile object makes it easy to map multiple names and emails to the same profile object to create "fuzzy" profiles and duplicates in your dataset. We will discuss how to perform fuzzy matching in the next section.

### Fuzzing Fake Names from Duplicates

If you noticed in our original data set we had the situation where we had a clear entity duplication: same email, but different names. In fact, the second name was simply the first initial and last name but you could imagine other situations like nicknames ("Bill" instead of "William"), or having both work and personal emails in the dataset. The fuzzy profile objects we generated in the last section allow us to maintain a mapping of all name parts to generated fake names, but we need some way to be able to detect duplicates and combine their profile: enter the `fuzzywuzzy` module.

    $ pip install fuzzywuzzy python-Levenshtein

Similar to how we did the domain mapping, we're going to pass through the entire dataset and look for similar name, email pairs and propose them to the user. If the user thinks they're duplicates, then we'll merge them together into a single profile, and use the mappings as we anonymize. Although I won't go through an entire object to do this as with the domain map, this is also something you can save to disk and load on demand for multiple anonymization passes and to include user based edits.

The first step is to get pairs, and eliminate exact duplicates. To do this we'll create a hashable data structure for our profiles using a `namedtuple`.

```python
from collections import namedtuple
from itertools import combinations

Person = namedtuple('Person', 'name, email')


def pairs_from_rows(rows):
    """
    Expects rows of dictionaries with name and email keys.
    """
    # Create a set of person tuples (no exact duplicates)
    people = set([
        Person(row['name'], row['email']) for row in rows
    ])

    # Yield ordered pairs of people objects without replacement
    for pair in combinations(people, 2):
        yield pair
```

The `namedtuple` is an immutable data structure that is compact, efficient, and allows us to access properties by name. Because it is immutable it is also hashable (unlike mutable dictionaries), meaning we can use it as keys in sets and dictionaries. This is important, because the first thing our `pairs_from_rows` function does is eliminate exact matches by creating a set of `Person` tuples. We then use the `combinations` function in `itertools` to generate every pair without replacement.

The next step is to figure out how similar each pair is. To do this we'll use the `fuzzywuzzy` library to come up with a partial ratio score: the mean of the similarity of the names and the emails for each pair:

```python
from fuzzywuzzy import fuzz
from functools import partial

def normalize(value, email=False):
    """
    Make everything lowercase and remove spaces.
    If email, only take the username portion to compare.
    """
    if email:
        value = value.split("@")[0]
    return value.lower().replace(" ", "")


def person_similarity(pair):
    """
    Returns the mean of the normalized partial ratio scores.
    """
    # Normalize the names and the emails
    names = map(normalize, [p.name for p in pair])
    email = map(
        partial(normalize, email=True), [p.email for p in pair]
    )

    # Compute the partial ratio scores for both names and emails
    scores = [
        fuzz.partial_ratio(a, b) for a, b in [names, emails]
    ]

    # Return the mean score of the pair
    return float(sum(scores)) / len(scores)
```

The score will be between 0 (no similarity) and 100 (exact match), though hopefully you won't get any scores of 100 since we eliminated exact matches above. For example:

```python
>>> person_similarity([
...     Person('John Lennon', 'john.lennon@gmail.com'),
...     Person('J. Lennon', 'jlennon@example.org')
... ])
80.5
```

The fuzzing process will go through your entire dataset, and create pairs of people it finds and compute their similarity score. Filter all pairs except for scores that meet a threshold (say, 50) then propose them to the user to decide if they're duplicates in descending score order. When a duplicate is found, merge the profile object to map the new names and emails together.

## Conclusion

Anonymization of datasets is a critical method to promote the exploration and practice of data science through open data. Fake data generators that already exist give us the opportunity to ensure that private data is obfuscated. This issue becomes how to leverage these fake data generators while still maintaining a high quality dataset with semantic relations preserved for further analysis. As we've seen throughout the post, even just the anonymization of just two fields, name and email can lead to potential problems.

This problem, and the code in this post are associated with a real case study. For District Data Labs' Entity Resolution Research Lab<sup><small>[3](#apd-footnote-3)</small></sup> I wanted to create a dataset that removed PII of DDL members while maintaining duplicates and structure to study entity resolution. The source dataset was 1,343 records in CSV form and contained name and emails that I wanted to anonymize.

Using the strategy I mentioned for domain name mapping, the dataset contained 245 distinct domain names, 185 of which were hapax legomena (appeared only once). There was a definite long tail, as the first 20 or so most frequent domains were the majority of the records. Once I generated the whitelist as above, I manually edited the mappings to ensure that there were no duplicates and that major work domains were &ldquo;professional enough&rdquo;.

Using the fuzzy matching process was also a bear. It took on average, 28 seconds to compute the pairwise scores. Using a threshold score of 50, I was proposed 5,110 duplicates (out of a possible 901,153 combinations). I went through 354 entries (until the score was below 65) and was satisfied that I covered many of the duplicates in the dataset.

In the end the dataset that I anonymized was of a high quality. It obfuscated personally identifying information like name and email and I'm happy to make the data set public. Of course, you could reverse the some of the information in the dataset. For example, I'm listed in the dataset, and one of the records indicates a relationship between a fake user and a blog post, which I'm on record as having written. However, even though you can figure out who I am and what else I've done in the dataset, you wouldn't be able to use it to extract my email address, which was the goal.

In the end, anonymizing a dataset is a lot of work, with a lot of gotchas and hoops to jump through. However, I hope you will agree that it is invaluable in an open data context. By sharing data, resources, and tools we can use many eyes to provide multiple insights and to drive data science forward.

### Footnotes

<a name="apd-footnote-1">1.</a> [Anonymize](http://www.google.com/search?q=define:anonymize): remove identifying particulars from (test results) for statistical or other purposes.

<a name="apd-footnote-2">2.</a> [Entity Resolution](http://www.slideshare.net/BenjaminBengfort/a-primer-on-entity-resolution): tools or techniques that identify, group, and link digital mentions or manifestations of some object in the real world.

<a name="apd-footnote-3">3.</a> [DDL Research Labs](http://www.districtdatalabs.com/research-lab) is an applied research program intended to develop novel, innovative data science solutions towards practical applications.
