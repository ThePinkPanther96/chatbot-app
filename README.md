# Magabot EKS Deployment with Datadog Monitoring

This project deploys the **Magabot application** (iPhone, Android, desktop services) on an **Amazon EKS cluster**, exposes it through an **AWS ALB ingress**, and integrates monitoring with the **Datadog Agent**.
---

## Repository Structure
```
.
├── app/                    # Flask application source
├── eks/
│   ├── eks-config.yaml      # EKS cluster definition for eksctl
│   ├── deployments/         # Kubernetes manifests for workloads
│   │   ├── 01-ns.yaml
│   │   ├── 02-iphone.yaml
│   │   ├── 03-android.yaml
│   │   ├── 04-desktop.yaml
│   │   └── 05-ingress.yaml
│   └── datadog/datadog-values.yaml  # Datadog Helm chart values
├── iam/iam_policy.json      # IAM policy for ALB controller
├── tests/                   # Test suite for the app
├── Dockerfile
├── DOCKER_VARS
└── README.md
```

---
## 1. Create the EKS Cluster

We use [`eksctl`](https://eksctl.io) with a declarative config:

```sh
eksctl create cluster -f eks/eks-config.yaml
