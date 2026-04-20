# kubernetes-cp

Kubernetes manifests for deploying Corridor Platform with Kustomize.

## Quickstart

1. Get the docker credentials from the Corridor Team - Contact <support@corridorplatforms.com>
2. Create a kubernetes secret with the docker credentials
3. Deploy the services (Note: For more customized setups, check the Configurations section below)
4. Verify the rollout

```bash
# 1. Copy the provided docker credentials json file to /tmp/corridor-registry-key.json (or a preferred path)

# 2. Create a kubernetes secret with the docker credentials
kubectl create secret docker-registry corridor-registry-secret \
  --docker-server=us-central1-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password="$(cat /tmp/corridor-registry-key.json)" \
  --namespace corridor

# 3. Deploy the services (NOTE: Use --dry-run=server for safety)
kubectl apply -k shared/redis
kubectl apply -k overlays/corridor

# 4. Verify rollout
kubectl get pods -n corridor
kubectl get svc -n corridor
kubectl get ingress -n corridor
kubectl get pods -n shared
kubectl get svc -n shared
```

## Architecture

The deployment architecture is the following:

- `corridor-app`: Primary API and Web application which serves the platform pages
- `corridor-worker`: Background worker process for heavy execution tasks
- `corridor-jupyter`: Jupyter/JupyterHub-facing service for ad-hoc analytics
- Shared persistent volumes for data, uploads, notebooks, Jupyter state, and backups
- A single ingress which routes `/` to the app-service and `/jupyter` to jupyter-service

## Cloud Compatibility

This repo is cloud agnostic.

It can be used on any Kubernetes cluster, including managed Kubernetes offerings such
as GKE from Google Cloud, EKS from AWS, AKS from Azure, OpenShift from RedHat, etc.

## Layout

```text
base/                Reusable application manifests
shared/redis/        Shared Redis deployment for one or more Corridor environments
overlays/corridor/   Minimal deployable overlay with placeholder configuration
```

It is possible to host multiple instances of corridor - for example:
`overlays/prod`, `overlays/staging`, `overlays/dev`. Or `overlays/team1` and `/overlays/team2`

## Configure

Feel free to configure the kubernetes setup based on your needs. Some common configurations are:

- By default the `kustomization.yaml` uses the `latest` tag. To use a older version of Corridor,
  set the docker image tag in `overlays/corridor/kustomization.yaml` > `newTag` variable.
- Set the public hostname based on your egress domain name in
  `overlays/corridor/kustomization.yaml`
- Set database, Redis, and application-specific settings in
  `overlays/corridor/configs/api_config.py`
- If your cluster uses a different RWX storage class, update the PVC patches in
  `overlays/corridor/kustomization.yaml`.
- Configure TLS secret keys etc in `base/ingress.yml`
- Configure other nginx configs like gzip/timeout etc. in `base/ingress.yml`
- Change Memory requests and limits in the respective `base/*.yml` files for that service.

## FAQs

**My pod is showing `ImagePullBackOff`**

If your pod events show `ImagePullBackOff` or registry authorization errors -> The
image authentication is likely the culprit. Double check if the correct docker credentials
are added to the kubernetes secret

**App is taking a long time to start**

The app deployment runs a database migration in an init container before the main API starts.
This can be decoupled to reduce restart time.
