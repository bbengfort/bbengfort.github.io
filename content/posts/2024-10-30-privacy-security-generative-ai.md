---
title: "Privacy and Security in the Age of Generative AI"
slug: "privacy-security-generative-ai"
date: "2024-10-30T11:35:00-07:00"
draft: false
categories: presentations
showtoc: false
---

[Privacy and Security in the Age of Generative AI](https://odsc.com/speakers/privacy-and-security-in-the-age-of-generative-ai/) is a talk that I gave at ODSC West 2024 in Burlingame, California. The slides of the talk are below:

{{< slideshare id="272867721" >}}

An updated presentation that I gave at C4AI on April 15, 2025 in Columbia, Maryland is below:

{{< slideshare id="278029566" >}}

### Abstract

From sensitive data leakage to prompt injection and zero-click worms, LLMs and generative models are the new cyber battleground for hackers. As more AI models are deployed in production, data scientists and ML engineers can't ignore these problems. The good news is that we can influence privacy and security in the machine learning lifecycle using data specific techniques. In this talk, we'll review some of the newest security concerns affecting LLMs and deep learning models and learn how to embed privacy into model training with ACLs and differential privacy, secure text generation and function-calling interfaces, and even leverage models to defend other models.

### Session Outline:

1. Security Concerns in Generative AI (6 minutes)
2. Data Access Controls for MLOps (6 minutes)
3. Building Privacy into Models (4 minutes)
4. LLM Model Evaluation (4 minutes)
5. Security Context for TGI and Function Calling (6 minutes)
6. Can Models Secure Models? (4 minutes)

### Learning Objectives:

Generative AI is an amazing interface for human users to better access the huge amounts of data with natural language queries. However, as AI becomes more important in automating repetitive, inconsistent, and boring tasks it has also become a target for hackers and malicious actors.

Image modification attacks such as modifying pixels in an image or adding stickers to signs can dramatically influence the output of computer vision systems and classifiers: usually to cause harmful actions to occur (e.g. to cause a vehicle to change lanes or for a fake driver's license to be recognized). Prompt injection attacks are used to manipulate LLMs into leaking sensitive data or spread misinformation. Researchers have even recently shown that AI worms are possible that target generative AI systems through adversarial self-replicating prompts.

As data scientists, we already have a lot of concerns from model quality and generalization to bias and fairness in our outputs; do we really need to take on security and privacy also? Data scientists and machine learning engineers use data to build data products for our users. Generative AI attacks are based on data, and therefore it is squarely in our purview as data scientists to ensure that we create high quality data pipelines and models that preserve the security and privacy of our users and organizations when used in combination with application security techniques.

In this talk we will explore data-driven techniques for privacy and security that will augment the security best practices of the application and product teams we belong to.

We know that the quality of a model is based on the data, so to is the security of the model. We'll explore the use of data access controls to influence model training and inferencing. We'll also look at algorithmic approaches such as differential privacy to prevent model leakage. Finally we'll explore how to combine security context and awareness in text generation inferences and function calling LLMs.

At the end of the the talk we'll touch on an open question for security researchers: can AI models be used to enhance the security of other models and more rapidly detect emergent threats?