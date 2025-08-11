---
source: "https://stackoverflow.com/questions/67388923/how-to-secure-the-environment-repo-in-a-gitops-setup"
title: "How to secure the environment repo in a GitOps setup?"
topic: ["kubernetes", "continuous-integration", "continuous-deployment", "continuous-delivery", "gitops"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: hai huang (asker), Jonas"
---

# RAW_THREAD

How to secure the environment repo in a GitOps setup?

Asked May 4, 2021 at 16:51 • Modified May 4, 2021 • Viewed 232 times
Part of CI/CD Collective

Score: 0

In a GitOps setting, there are usually two repositories - a code repo and an environment repo. My understanding is that there are some security benefits in separating the repos so developers only need to be given access to the code repo, and environment repo's write access can be limited to only the CI/CD tools. As the environment repo is the source-of-truth in GitOps, this is claimed to be more secure as it minimizes human involvement in the process.

My questions are:

If the assumption above is correct, what CI/CD tools should be given access to the environment repo? Is it just the pipeline tools such as Tekton (CI) and Flux (CD), or can other tools invoked by the pipelines be also included in this "trusted circle"? What are the best practices around securing the environment repo in GitOps?

What is the thought process around sync'ing intermediate / dynamic states of the cluster back to the environment repo, e.g., number of replicas in a deployment controlled by an HPA, network routing controlled by a service mesh provider (e.g., Istio), etc.? From what I have seen, most of the CD pipelines are only doing uni-directional sync from the environment repo to the cluster, and never the other way around.

But there could be benefit in keeping some intermediate states, e.g., in case one needs to re-create other clusters from the environment repo.

Tags: kubernetes • continuous-integration • continuous-deployment • continuous-delivery • gitops

1 Answer
Answer 1
Score: 1 • Answered May 4, 2021 at 17:12 by Jonas

there are usually two repositories - a code repo and an environment repo. My understanding is that there are some security benefits in separating the repos so developers only need to be given access to the code repo, and environment repo's write access can be limited to only the CI/CD tools.

It is a good practice to have a separate code repo and configuration repo when practicing any form of Continuous Delivery. This is described in the "classical" Continuous Delivery book. The reason is that the two repos change in a different cycle, e.g. first the code is changed and after a pipeline has verified changes, an updated to config repo can be made, with e.g. Image Digest.

The developer team should have access to both repos. They need to be able to change the code, and they need to be able to change the app configuration for different environments. A build tool, e.g. from a Tekton pipeline may only need write access to config repo, but read access to both repos.

What is the thought process around sync'ing intermediate / dynamic states of the cluster back to the environment repo, e.g., number of replicas in a deployment controlled by an HPA, network routing controlled by a service mesh provider (e.g., Istio), etc.? From what I have seen, most of the CD pipelines are only doing uni-directional sync from the environment repo to the cluster, and never the other way around.

Try to avoid sync'ing "current state" back to a Git repo, it will only be complicated. For you, it is only valueable to keep the "desired state" in a repo - it is useful to see e.g. who changes what an when - but also for disaster recovery or to create a new identical cluster.
