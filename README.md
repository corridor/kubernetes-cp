# kubernetes-cp

Kubernetes manifests for deploying Corridor Platform with Kustomize.

The deployment architecture is based on the current Corridor runtime layout:

- `corridor-app`: primary API and web application
- `corridor-worker`: background worker process
- `corridor-jupyter`: Jupyter/JupyterHub-facing service
- shared persistent volumes for app data, uploads, notebooks, Jupyter state, and databases
- a single ingress routing `/` to the app and `/jupyter` to Jupyter

This repo is cloud agnostic. It can be used on any Kubernetes cluster, including
managed Kubernetes offerings such as GKE, EKS, and AKS, as long as the cluster
provides:

- an ingress controller
- a TLS issuer or existing TLS secret
- a `ReadWriteMany`-capable storage class
- an image pull secret for the container registry you use

## Layout

```text
base/               Reusable application manifests
shared/redis/       Shared Redis deployment for one or more Corridor environments
overlays/example/   Minimal deployable overlay with placeholder configuration
```

## Configure

Update these files before deployment:

- `shared/redis/kustomization.yaml`
  - review the shared namespace if you want Redis in a different namespace
- `overlays/example/kustomization.yaml`
  - set the namespace
  - set the application image for `corridor-app` and `corridor-worker`
    - currently set to use Google Artifact Registry (Hosted by `Corridor Platforms`)
  - set the Jupyter image to `corridor-jupyter`
    - currently set to use Google Artifact Registry (Hosted by `Corridor Platforms`)
  - set the public hostname
- `overlays/example/configs/api_config.py`
  - set database, Redis, and application-specific settings
- `overlays/example/configs/jupyter_server_config.py`
  - set Jupyter runtime settings if needed
- `overlays/example/configs/jupyterhub_config.py`
  - set API connectivity and any JupyterHub-specific settings

If your cluster uses a different RWX storage class, update the PVC patches in
`overlays/example/kustomization.yaml`.

Redis manifests are kept under `shared/redis` because a single Redis deployment
can be shared across multiple Corridor deployments instead of running one Redis
instance per overlay.

## Deploy

If you want to use the shared Redis instance, deploy it first:

```bash
kubectl apply -k shared/redis
```

Create the image pull secret in the target namespace if required:

```bash
kubectl create namespace <namespace>
kubectl create secret docker-registry registry-secret \
  --docker-server=<registry-host> \
  --docker-username=<username> \
  --docker-password=<password> \
  --namespace <namespace>
```

Render and apply the overlay:

```bash
kubectl apply -k overlays/example
```

Verify rollout:

```bash
kubectl get pods -n <namespace>
kubectl get svc -n <namespace>
kubectl get ingress -n <namespace>
kubectl get pods -n shared
kubectl get svc -n shared
```

## Notes

- The base manifests assume the application image contains the `corridor-api`,
  and `corridor-worker` entrypoints.
- Jupyter uses a separate image:
  `us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-jupyter`.
  Update the overlay so the Jupyter deployment points at that image before
  deployment.
- The app deployment runs a database migration in an init container before the
  main API starts.
- The ingress manifest references `cert-manager.io/cluster-issuer: letsencrypt-prod`;
  adjust or remove that annotation if your cluster handles TLS differently.
- The `overlays/example/` configuration is intentionally minimal and uses
  placeholder values. It is meant to be copied or edited before real deployment.
