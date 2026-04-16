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
    - currently:
      `us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-api:<tag>`
  - set the Jupyter image for `corridor-jupyter`
    - currently:
      `us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-jupyter:<tag>`
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

## Accessing GAR Images

Clients pull private images from Google Artifact Registry using a read-only
service account key provided by Corridor.

### 1. Receive GAR credentials and image references

Corridor must provide:

- a `key.json` service account key with read access to the required GAR repository
- the application image URL and tag for `corridor-app` and `corridor-worker`
- the Jupyter image URL and tag for `corridor-jupyter`

The application image currently uses:

```text
us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-api:<tag>
```

Jupyter currently uses:

```text
us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-jupyter:<tag>
```

### 2. Create a pull secret in the target namespace

Use the GAR service account key to create a Docker registry secret:

```bash
kubectl create secret docker-registry gar-pull-secret \
  --docker-server=<gar-registry-host> \
  --docker-username=_json_key \
  --docker-password="$(cat key.json)" \
  --namespace <namespace>
```

Set `--docker-server` to the registry host from the image URL, such as
`us-west1-docker.pkg.dev` or `us-central1-docker.pkg.dev`.

If Jupyter is hosted in a different GAR registry host from the app image,
create an additional secret for that host or use a combined Docker config secret.

### 3. Reference the pull secret from workloads

The manifests in this repo expect an image pull secret in the target namespace.
You can either:

- create the secret as `registry-secret`, or
- update the manifests to use `gar-pull-secret`

### 4. Point the overlay at the GAR images

Update `overlays/example/kustomization.yaml` so the app and worker deployments
use the application GAR image:

```text
us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-api:<tag>
```

Update the Jupyter deployment so it uses the Jupyter-specific GAR image:

```text
us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-jupyter:<tag>
```

### 5. Verify image access before rollout

After creating the pull secret and updating the image references, render or apply
the overlay and check for image pull failures:

```bash
kubectl apply -k overlays/example
kubectl get pods -n <namespace>
kubectl describe pod -n <namespace> <pod-name>
```

If image authentication is wrong, pod events will show `ImagePullBackOff` or
registry authorization errors.

## Deploy

If you want to use the shared Redis instance, deploy it first:

```bash
kubectl apply -k shared/redis
```

Create the target namespace and GAR pull secret before deployment. Follow the
steps in `Accessing GAR Images` above. If you use a secret name other than
`registry-secret`, update the manifests to match.

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

- The app and worker deployments use the application image:
  `us-central1-docker.pkg.dev/heroic-oven-269206/corridor/cp-api:<tag>`.
  That image is expected to contain the `corridor-api` and `corridor-worker`
  entrypoints.
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
