---
source: "https://stackoverflow.com/questions/76989574/pass-in-array-of-objects-to-helm"
title: "Pass in array of objects to Helm"
topic: ["kubernetes-helm", "argocd"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: SledgeHammer (asker),David Maze, N37, Orifjon"
---
# RAW_THREAD

Asked 1 year, 11 months ago • Modified 1 year, 2 months ago • Viewed 3k times
Part of CI/CD Collective

Score: 1

I am new to Helm and see Helm chart values.yml with entries like:

makefile
Copy code
extraEmptyDirMounts: []
  # - name: provisioning-notifiers
  #   mountPath: /etc/grafana/provisioning/notifiers
I can't for the life of me figure out how to pass that in through the Helm overrides in the format of:

yaml
Copy code
spec:
  source:
    helm:
      parameters:
      - name: extraEmptyDirMounts
        value: ???
I've Googled around and am yet to find a clear example of this since it seems pretty common.

Somehow, this array of objects is supposed to be encoded in the single value parameter.

Tags: kubernetes-helm • argocd

Comments

That spec: { source: { helm: } } syntax isn't familiar to me; what tool does it go with? — David Maze • Aug 28, 2023 at 9:46

@DavidMaze its a patch file yaml, but the CICD tool I'm using is ArgoCD. I think its basically the same format as the SET syntax where you can set Key/Value pairs. I did get it work with [] syntax, but that seems overly verbose. - name: volumes[0].hostPath.path value: /run/desktop/mnt/host/c/users/xxx/.localstack/scripts - name: volumes[0].name value: localstack-scripts — SledgeHammer • Aug 28, 2023 at 15:30

3 Answers
Answer 1
Score: 5 • Answered Aug 28, 2023 at 15:58 by David Maze

Argo CD supports passing in structured Helm values (valuesObject), either as a YAML object or as an encoded string. I'd use valuesObject: over parameters: here.

yaml
Copy code
spec:
  source:
    helm:
      valuesObject:
        extraEmptyDirMounts:
          - name: provisioning-notifiers
            mountPath: /etc/grafana/provisioning/notifiers
parameters: replicates the helm install --set syntax. This is a little bit unusual format, and you can't effectively use it to provide an array of nested objects (it's possible but rather unpleasant).

Comments

Interesting! If this works, it'll definitely be cleaner then the parameters syntax! — SledgeHammer • Aug 28, 2023 at 16:31

It worked. Much cleaner then the parameters syntax. Thanks! It does "break" the UI though :), by not showing the overrides, but... — SledgeHammer • Aug 28, 2023 at 17:01

Answer 2
Score: 1 • Answered May 17, 2024 at 4:52 by N37

you can pass an array of objects like this:

yaml
Copy code
    helm:
      parameters:
        - name: extraEmptyDirMounts[0].name
          value: provisioning-notifiers
        - name: extraEmptyDirMounts[0].mountPath
          value: "/etc/grafana/provisioning/notifiers"
        - name: extraEmptyDirMounts[1].name
          value: somethings...
          .......
Answer 3
Score: 0 • Answered Aug 28, 2023 at 2:00 by Orifjon

Your question is a bit unclear, do you want to add multiple items to extraEmptyDirMounts? If yes then you can repeat commented out part with different values.

For example

yaml
Copy code
extraEmptyDirMounts:
  - name: provisioning-notifiers
    mountPath: /etc/grafana/provisioning/notifiers
  - name: another-entry
    mountPath: /etc/another/path/value
Comments

No, its for Helm parameter overrides. I've updated the question. — SledgeHammer • Aug 28, 2023 at 2:16

