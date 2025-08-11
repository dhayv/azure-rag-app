---
source: "https://stackoverflow.com/questions/74923859/argocd-why-helm-app-not-applying-values-yml"
title: "argocd: why helm app not applying values.yml"
topic: ["kubernetes", "kubernetes-helm", "argocd", "gitops", "argo"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: Mohamed (asker), HiroCereal, ishuar"
---

# RAW_THREAD

argocd: why helm app not applying values.yml

Asked Dec 26, 2022 at 20:44 • Edited Dec 27, 2022 at 13:39 • Viewed 11k times
Part of CI/CD Collective

Score: 2

I would like to install a helm release using argocd, i defined a helm app declaratively like the following :

yaml
Copy code
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: moon
  namespace: argocd
spec:
  project: aerokube
  source:
    chart: moon2
    repoURL: https://charts.aerokube.com/
    targetRevision: 2.4.0
    helm:
      valueFiles:
      - values.yml
  destination:
    server: "https://kubernetes.default.svc"
    namespace: moon1
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
Where my values.yml:

yaml
Copy code
customIngress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt"   
  ingressClassName: nginx
  host: moon3.benighil-mohamed.com
  tls:
  - secretName: moon-tls
    hosts:
    - moon3.benighil-mohamed.com
configs:
  default:
    containers:
      vnc-server:
        repository: quay.io/aerokube/vnc-server
        resources:
          limits:
            cpu: 400m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 512Mi
Notice, the app does not take values.yml into consideration, and i get the following error:

bash
Copy code
rpc error: code = Unknown desc = Manifest generation error (cached): `helm template .
--name-template moon --namespace moon1 --kube-version 1.23 --values /tmp/.../moon2/values.yml ...` failed exit status 1: Error: open /tmp/.../moon2/values.yml: no such file or directory
Notice both application.yml and values.yml are located in the same directory on my local machine…

Tags: kubernetes • kubernetes-helm • argocd • gitops • argo

Comments

Can you amend your question with more infos please … I presume you're receiving the error from the argocd pod right? — Mike • Dec 27, 2022 at 10:20

i added the structure as you suggested — Mohamed • Dec 27, 2022 at 13:39

Can you run helm template command locally, does it work? — taleodor • Dec 28, 2022 at 2:14

ArgoCD searches for the values.yaml file in the URL you specified and not "locally" … try a repo with the desired values.yaml … — Mike • Dec 28, 2022 at 9:37

Okay i have understood. But is it possible to update the default values.yml without pulling & untar the chart ? — Mohamed • Dec 28, 2022 at 10:49

2 Answers
Answer 1
Score: 6 • Answered Jan 2, 2023 at 15:37 by HiroCereal

Cleanest way to achieve what you want is using the remote chart as dependency:

Chart.yaml

yaml
Copy code
name: mychartname
version: 1.0.0
apiVersion: v2
dependencies:
  - name: moon2
    version: "2.4.0"
    repository: "https://charts.aerokube.com/"
And overriding its values like this:

values.yaml

yaml
Copy code
moon2:
  customIngress:
    enabled: true
    annotations:
      cert-manager.io/cluster-issuer: "letsencrypt"   
    ingressClassName: nginx
    host: moon3.benighil-mohamed.com
    tls:
    - secretName: moon-tls
      hosts:
      - moon3.benighil-mohamed.com
  configs:
    default:
      containers:
        vnc-server:
          repository: quay.io/aerokube/vnc-server
          resources:
            limits:
              cpu: 400m
              memory: 512Mi
            requests:
              cpu: 200m
              memory: 512Mi
Pay attention to this file. You need to create a key in your values file with the same name as the dependency (moon2 in your case), and indent the values you want to override one level.

You need to upload both of these files to a repository and point your ArgoCD application URL to this repository.

This has the advantage that whenever the upstream helm chart gets updated, all you need to do is increase the version in Chart.yaml

Comments

This actually solved the problem … This should rather be documented … — Jauyzed • Dec 18, 2024 at 0:12

Answer 2
Score: 1 • Answered Jan 2, 2023 at 20:21 by ishuar • Edited Jan 2, 2023 at 22:45 by BDL

This can be achieved without an umbrella Chart also if you are fine with inline values definitions in the argocd application.

Basically, you can check out below file in your GitRepo and then configure argocd to track this file/argocd application. In the future whenever you have to update this application you can directly edit the definitions of the explicit values in this file.

yaml
Copy code
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: moon
  namespace: argocd
spec:
  project: aerokube
  source:
    chart: moon2
    repoURL: https://charts.aerokube.com/
    targetRevision: 2.4.0
    helm:
      values: |
        customIngress:
          enabled: true
          annotations:
            cert-manager.io/cluster-issuer: "letsencrypt"   
          ingressClassName: nginx
          host: moon3.benighil-mohamed.com
          tls:
          - secretName: moon-tls
            hosts:
            - moon3.benighil-mohamed.com
        configs:
          default:
            containers:
              vnc-server:
                repository: quay.io/aerokube/vnc-server
                resources:
                  limits:
                    cpu: 400m
                    memory: 512Mi
                  requests:
                    cpu: 200m
                    memory: 512Mi
  destination:
    server: "https://kubernetes.default.svc"
    namespace: moon1
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
This is only about personal preference if you do not want an Umbrella Chart in your git repo. However, I personally would go with the Umbrella Chart deployment.