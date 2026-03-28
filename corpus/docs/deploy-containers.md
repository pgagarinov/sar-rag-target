# FluxAPI Container Deployment

FluxAPI runs your applications in containers. The platform manages container orchestration, scaling, networking, and health checks. You provide a container image; FluxAPI handles everything else.

## Container Registry

FluxAPI includes a private container registry at `registry.fluxapi.io`. Push images using standard Docker commands after authenticating: `docker login registry.fluxapi.io -u $FLUX_REGISTRY_USER -p $FLUX_REGISTRY_TOKEN`. Images are tagged per environment and version: `registry.fluxapi.io/{project}/{service}:{env}-{version}`. The registry supports multi-architecture images (amd64, arm64). Image scanning runs automatically on push, checking for known CVEs. Images with critical vulnerabilities are flagged but not blocked by default — enable blocking via **Settings > Security > Image Policy**. Registry storage is unlimited on paid plans and 5GB on starter plans. Images are retained for 90 days after last pull, then garbage-collected.

## Dockerfile Best Practices

Optimize your Dockerfile for FluxAPI deployment. Use multi-stage builds to minimize image size — separate build dependencies from runtime. Pin base image versions for reproducibility: `FROM python:3.12-slim@sha256:...`. Run as non-root user: `RUN useradd -r appuser && USER appuser`. Include a health check endpoint: `HEALTHCHECK CMD curl -f http://localhost:8080/health`. Minimize layers by combining RUN commands. Copy dependency manifests first for better layer caching: `COPY requirements.txt . && RUN pip install -r requirements.txt`. Set proper signal handling with `ENTRYPOINT ["tini", "--"]` or handle SIGTERM in your application. The FluxAPI build service also supports buildpacks — push source code and FluxAPI builds the container automatically.

## Scaling Configuration

Configure horizontal and vertical scaling via `PUT /v2/deployments/{id}/scaling`. Horizontal scaling adjusts the number of container replicas based on metrics. Set `min_replicas` (default 1), `max_replicas` (default 10), and scaling triggers. Built-in triggers include CPU utilization (default threshold 70%), memory utilization (80%), request rate, and response latency. Custom metrics triggers use the `POST /v2/metrics/custom` endpoint. Vertical scaling adjusts CPU and memory per container. Available sizes: `small` (0.25 vCPU, 256MB), `medium` (1 vCPU, 1GB), `large` (4 vCPU, 4GB), `xlarge` (8 vCPU, 16GB). Scale-up takes 15-30 seconds for new replicas. Scale-down has a 5-minute cooldown to prevent flapping. During scaling events, traffic is automatically load-balanced across healthy replicas.

## Container Environment and Networking

Containers receive environment variables from the FluxAPI environment configuration system. The runtime injects `FLUX_ENV`, `FLUX_REGION`, `FLUX_SERVICE_NAME`, and `PORT` automatically. Containers must listen on the port specified by `PORT` (default 8080). Internal service-to-service communication uses the service mesh at `{service-name}.internal.fluxapi.io`. External traffic routes through the FluxAPI load balancer with automatic TLS termination. Health checks run every 10 seconds — three consecutive failures trigger container restart.
