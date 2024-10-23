---
title: "Smart Global Replication Using Reinforcement Learning"
slug: "smart-global-replication-using-reinforcement-learning"
date: "2023-11-07T12:00:00-05:00"
draft: false
categories: presentations
showtoc: false
---

[Smart Global Replication using Reinforcement Learning](https://kccncna2023.sched.com/event/21d4640540a0961019d201de8ec2fd5e) is a talk that I gave at KubeCon + CloudNative North America 2023 in Chicago, IL. The video of the talk is below:

{{< youtube YTF2dXNhFzI >}}

### Description

There are many great reasons to replicate data across Kubernetes clusters in different geographic regions: e.g. for disaster recovery and to ensure the best possible user experiences. Unfortunately, global replication is not easy; not just because of the difficulty in consistency reasoning that it introduces, but also due to the increased cost of provisioning multiple volumes that exponentially duplicate ingress and egress. Wouldn't it be great if our systems could learn the optimal placement of storage blocks so that total replication was not necessary? Wouldn't it be even better if our replication messaging was reduced ensuring communication only between the minimally necessary set of storage nodes? We show a system that uses multi-armed bandits to perform such an optimization; dynamically adjusting how data is replicated based on usage. We demonstrate the savings achieved and system performance using a real world system: the TRISA Global Travel Rule Compliance Directory.