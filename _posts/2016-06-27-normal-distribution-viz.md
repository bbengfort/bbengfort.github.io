---
layout: post
title:  "Visualizing Normal Distributions"
date:   2016-06-27 08:27:07 -0400
categories: snippets
---

Normal distributions are the backbone of random number generation for simulation. By selecting a mean (&mu;) and standard deviation (&sigma;) you can generate simulated data representative of the types of models you're trying to build (and certainly better than simple uniform random number generators). However, you might already be able to tell that selecting &mu; and &sigma; is a little backward! Typically these metrics are computed from data, not used to describe data. As a result, utilities for tuning the behavior of your random number generators are simply not discussed.

I wanted to be able to quickly and easily predict what would happen as I varied &mu; and &sigma; in my distribution. These are easy to think about: if you picture the normal curve, then &mu; describes where the middle of the curve is. If you want to have data centered around 100, then you would choose a &mu; of 100. Standard deviation describes how spread out the data is, or how tall or flat the normal curve is above the mean. A standard deviation of zero would be a spike right at the mean, where as a very high standard deviation will be extremely flat with a wide range.

Remembering that &plusmn;3&sigma; from the mean captures most of the data from the random generator, I set up creating a visual way to inspect the properties and behaviors of the normal generators I was creating. In particular, my goal is to visually inspect the range of the data, as well as the density of results. This helps debug issues in simulations. Therefore, I give you a normal distribution simulation:

<script src="https://gist.github.com/bbengfort/99413d0e48c4188b8076534e0dcfb835.js"></script>

By running this simply Python script:

```bash
$ python norm.py 12.0 2.0
```

You end up with visuals as follows:

![Normal curve with a mean of 12 and a standard deviation of 2]({{ site.base_url }}/assets/images/2016-06-27-small-sigma-curve.png)

Shifting the mean and increasing the standard deviation gives you the following:

```bash
$ python norm.py 14 12.4
```

Which, as you can see, definitely changes the scale of the domain of the random number generator!

![Normal curve with a mean of 14 and a standard deviation of 12.4]({{ site.base_url }}/assets/images/2016-06-27-big-sigma-curve.png)

It may be hard to see - but check out the domains of both axes to get a feel for the magnitude of that change! Now you have a simple and effective way to reason about how &mu; and &sigma; might change the way that random numbers are selected!
