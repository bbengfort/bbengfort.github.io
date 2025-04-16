---
title: "Practical Multi Armed Bandits"
slug: "practical-multi-armed-bandits"
date: "2025-04-18T12:05:00-04:00"
draft: true
categories: presentations
showtoc: false
---

[Practical Multi Armed Bandits](https://cfp.pydata.org/virginia2025/talk/XRXKDK/) is a talk that I gave at PyData VA 2025 in Charlottesville, Virginia. The slides of the talk are below:

{{< slideshare id="272867721" >}}

### Abstract

Multi-armed bandits are a reinforcement learning tool often used in environments where the cost or rewards of different choices are unknown or where those functions may change over time. The good news is that as far as implementation goes, bandits are surprisingly easy to implement; however, in practice, the difficulty comes from defining a reward function that best targets your specific use case. In this talk, we will discuss how to use bandit algorithms effectively, taking note of practical strategies for experimental design and deployment of bandits in your applications.

### Description

Imagine a row of slot machines (often called one-armed bandits because of the lever on the side and the fact that they take your money) -- you know that one of them will pay out more than the others over time, but how do you figure out which one? This is the premise of the multi-armed bandit (MAB) problem, which has become a vital reinforcement learning technique used to balance the exploration-exploitation dilemma (e.g., at what point do you start exploiting the best choice to maximize your rewards instead of exploring for better options).

Multi-armed bandits are straightforward to implement: define your choices and assign each of them a probability distribution for selection. Each time a choice is made, the probability distribution for that choice is updated based on the outcome of a reward function. Easy right? The trick is in designing both your choices and your reward function in such a way that you capture the dynamics of your experimental environment, often a live environment that involves user behavior and other irregularities!

Things get more complicated when you have multiple agents - each of them with their own probability distributions. Here, you need to design the reward functions such that your desired behavior emerges from the collective interactions of each individual agent. The best type of complexity arises globally from many simple local interactions!

In this talk, we will learn how to implement multi-armed bandits and reward functions for three use cases: ordering a news feed, prioritizing tasks for a team in a sprint, and minimizing cloud costs for a distributed system. We'll focus on practical strategies for designing reward functions and dealing with change. At the end of this talk you should be ready and excited to implement bandit algorithms for your own data science problems!