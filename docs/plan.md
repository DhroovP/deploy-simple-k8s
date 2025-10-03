# High-Level Plan

## Goal

Deploy a web server using a single command.

## Breaking down the goal

1. Create a container image (Dockerfile, can switch to Paketo if time provides)
2. Create an EKS cluster
3. Push a container image to ECR
4. Deploy a web app to Kubernetes
5. Print the public address

## Scaffold

```tree
project/
  Makefile
  .env
  .gitignore
  deploy.py
  destroy.py
  Dockerfile
  README.md
  docs/
  app/ (Python Django)
  k8s/ (any Kubernetes manifests)
```

## Reasonings and Choices
1. Makefile allows for simplicity and dependency installs while being idemptonent. Avoids putting all logic into Python, and allows for easier loading of `.env`.

2. Python scripts will serve as a cleaner wrapper for what is effectively just command line statements under the hood. Easier to implement safety mechanisms like dry runs.

3. Dockerfile to create the container image.

3. k8s/ for Deployment and Service objects.