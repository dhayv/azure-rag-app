---
source: "https://stackoverflow.com/questions/69787413/application-not-showing-in-argocd-when-applying-yaml"
title: "Application not showing in ArgoCD when applying yaml"
topic: ["kubernetes", "deployment", "devops", "argocd", "gitops"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: Matt (asker), mehrdad.f, everspader, Anil Singh"
---

# RAW_THREAD

Application not showing in ArgoCD when applying yaml

Asked Oct 31, 2021 at 13:36 • Modified 1 year, 3 months ago • Viewed 26k times
Part of CI/CD Collective

Score: 11

I am trying to setup ArgoCD for gitops. I used the ArgoCD helm chart to deploy it to my local Docker Desktop Kubernetes cluster. I am trying to use the app of apps pattern for ArgoCD.

The problem is that when I apply the yaml to create the root app, nothing happens. Here is the yaml (created by the command helm template apps/ -n argocd from the my public repo https://github.com/gajewa/gitops):

yaml
Copy code
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  destination:
    server: http://kubernetes.default.svc
    namespace: argocd
  project: default
  source:
    path: apps/
    repoURL: https://github.com/gajewa/gitops.git
    targetRevision: HEAD
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
The resource is created but nothing in Argo UI actually happened. No application is visible. So I tried to create the app via the Web UI, even pasting the yaml in there. The application is created in the web ui and it seems to synchronise and see the repo with the yaml templates of prometheus and argo but it doesn't actually create the prometheus application in ArgoCD. And the prometheus part of the root app is forever progressing.

Screenshots omitted in text copy.

I thought maybe the CRD definitions are not present in the k8s cluster but I checked and they're there:

lua
Copy code
λ kubectl get crd
NAME                       CREATED AT
applications.argoproj.io   2021-10-30T16:27:07Z
appprojects.argoproj.io    2021-10-30T16:27:07Z
I've ran out of things to check why the apps aren't actually deployed. I was going by this tutorial: https://www.arthurkoziel.com/setting-up-argocd-with-helm/

Tags: kubernetes • deployment • devops • argocd • gitops

Comments

You should be able to click in the individual root/argocd/prometheus boxes and see the underlying applications. Have you tried that? — kazanaki • Dec 3, 2021 at 13:58

You said you apply the yaml to create the root app. How do you apply the yaml? Are you applying it in the right namespace? You can try to run kubectl get apps -A for all namespaces to see if you create it where needed. — Liviu Costea • Dec 6, 2021 at 11:10

I to have similar issue. And I do see kubectl get apps -A that they are created in namespace argocd and with the correct names. But it does not find custom project name. I do not want to use 'default' project. — Sanjeev • May 18, 2022 at 14:47

3 Answers
Answer 1
Score: 18 • Answered Jan 20, 2022 at 7:41 by mehrdad.f

The problem is you have to use the below code in your manifest file in metadata:

just please change the namespace with the name your argocd was deployed in that namespace. (default is argocd)

vbnet
Copy code
metadata:
  namespace: argocd
Comments

This was it for me. I didn't realise that the namespace of the ArgoCD Application CRD has to be the same as the namespace to which ArgoCD is deployed, otherwise it doesn't pick up the application. — Steven Gillies • Dec 1, 2023 at 17:33

Answer 2
Score: 0 • Answered Mar 3, 2022 at 16:07 by everspader

From another SO post: https://stackoverflow.com/a/70276193/13641680

It turns out that at the moment ArgoCD can only recognize application declarations made in ArgoCD namespace,

Related GitHub Issue

Comments

Is there any reason you duplicated the answer provided by @mehrdad.f 42 days before you? — TJ Zimmerman • Jul 11, 2022 at 23:24

It's not duplicated. It's an addition with more resources — everspader • Jul 12, 2022 at 11:50

You could have easily added those as comments on the first answer. — TJ Zimmerman • Jul 12, 2022 at 15:48

Answer 3
Score: 0 • Answered Apr 24, 2024 at 7:37 by Anil Singh

Hi i fixed this issue using below command using hard refress

sql
Copy code
argocd app get test --hard-refresh
more info https://github.com/argoproj/argo-cd/issues/9214