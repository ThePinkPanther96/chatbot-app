# Magabot EKS Deployment with Datadog Monitoring

This project deploys the **Magabot application** (iPhone, Android, desktop services) on an **Amazon EKS cluster**, exposes it through an **AWS ALB ingress**, and integrates monitoring with the **Datadog Agent**.
---

## Repository Structure
```
.
├── app/                             # Flask application source
├── eks/
│   ├── eks-config.yaml              # EKS cluster definition for eksctl
│   ├── deployments/                 # Kubernetes manifests for workloads
│   │   ├── 01-ns.yaml
│   │   ├── 02-iphone.yaml
│   │   ├── 03-android.yaml
│   │   ├── 04-desktop.yaml
│   │   └── 05-ingress.yaml
│   └── datadog/datadog-values.yaml  # Datadog Helm chart values
├── iam/iam_policy.json              # IAM policy for ALB controller
├── tests/                           # Test suite for the app
├── Dockerfile
├── DOCKER_VARS
└── README.md
```

---
## 1. Create the EKS Cluster

We use [`eksctl`](https://eksctl.io) with a declarative config:

```sh
eksctl create cluster -f eks/eks-config.yaml
```

**These provisions:**
	•	Cluster name: magabot-ingress
	•	Region: eu-central-1
	•	2 managed nodes (t3.small, min=2, max=4)
	•	IAM OIDC provider (required for IRSA)
	•	Private networking only (nodes get no public IPs)

---
## 2. AWS Load Balancer Controller

The ALB controller manages AWS Application Load Balancers for Kubernetes ingress resources.

Create IAM Service Account (IRSA):
```
eksctl create iamserviceaccount \
  --cluster=magabot-ingress \
  --namespace=magabot-ns \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::<YOUR_ACCOUNT_ID>:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --region=eu-central-1 \
  --approve
```
Install Controller with Helm:
```
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=magabot-ingress \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --version 1.13.0
```

## 3. Application Secrets

The application uses the OpenAI API. Create the secret once:
```
kubectl -n magabot-ns create secret generic openai \
  --from-literal=OPENAI_API_KEY='<YOUR_OPENAI_API_KEY>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

---
## 4. Deploy Magabot Workloads

Apply manifests in order:
```
kubectl apply -f eks/deployments/01-ns.yaml      # Namespace
kubectl apply -f eks/deployments/02-iphone.yaml
kubectl apply -f eks/deployments/03-android.yaml
kubectl apply -f eks/deployments/04-desktop.yaml
kubectl apply -f eks/deployments/05-ingress.yaml # Ingress + ALB
```

Check rollout:
```
kubectl -n magabot-ns rollout status deploy/iphone-deploy
kubectl -n magabot-ns rollout status deploy/android-deploy
kubectl -n magabot-ns rollout status deploy/desktop-deploy
```

Retrieve ALB hostname:
```
kubectl -n magabot-ns get ingress magabot-ingress \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'; echo
```

---
## 5. Datadog Integration

Namespace & Secrets:
```
kubectl create namespace datadog

kubectl -n datadog create secret generic datadog-api-key \
  --from-literal=api-key='<YOUR_DATADOG_API_KEY>'

kubectl -n datadog create secret generic datadog-app-key \
  --from-literal=app-key='<YOUR_DATADOG_APP_KEY>'
```

Install Datadog Agent via Helm:
```
helm repo add datadog https://helm.datadoghq.com
helm repo update

helm upgrade --install datadog datadog/datadog \
  -n datadog \
  -f eks/datadog/datadog-values.yaml
```

Verify: 
```
kubectl -n datadog rollout status daemonset/datadog
kubectl -n datadog rollout status deployment/datadog-cluster-agent
```

Check API key:
```
P=$(kubectl -n datadog get pods -l app=datadog -o jsonpath='{.items[0].metadata.name}')
kubectl -n datadog exec -it "$P" -c agent -- agent status | egrep -i 'cluster-name|site|API Key valid'
```

---
## 6. Validation

Application:
```
kubectl -n magabot-ns get pods -o wide
```
You should see 2 pods each for iphone, android, and desktop.

Ingress / ALB:
```
curl -I http://magabot.gal-rozman.com/
curl -I http://magabot.gal-rozman.com/iphone
curl -I http://magabot.gal-rozman.com/android
```
Should return HTTP 301 → HTTPS.

In Datadog, confirm workloads appear in the Datadog dashboard.

---
## Summary
	•	Cluster created with eksctl (eks/eks-config.yaml)
	•	ALB controller installed with Helm
	•	OpenAI secret created (openai)
	•	Workloads deployed (iphone, android, desktop)
	•	Ingress managed by ALB
	•	Datadog Agent + Cluster Agent installed and validated
