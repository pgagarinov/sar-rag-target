# FluxAPI Environment Configuration

FluxAPI supports multiple isolated environments for each project. Environments allow you to develop, test, and deploy with confidence by separating configuration and data across stages.

## Environment Types

Every FluxAPI project starts with three environments: `development`, `staging`, and `production`. Development is for local testing and experimentation — it has relaxed rate limits and verbose logging. Staging mirrors production configuration but uses isolated data — use it for integration testing and pre-release validation. Production is the live environment serving real traffic — it has strict security controls and optimized performance settings. You can create up to 5 custom environments (e.g., `qa`, `demo`, `canary`) via `POST /v2/environments` with a name and base configuration. Each environment has its own API keys, database connections, and secret values.

## Environment Variables

Environment variables configure runtime behavior without code changes. Set variables via the dashboard under **Environments > Variables** or via `PUT /v2/environments/{env}/variables`. Variables are key-value string pairs. Keys must match the pattern `[A-Z][A-Z0-9_]*` (uppercase with underscores). Variable values have a maximum length of 4096 characters. System variables prefixed with `FLUX_` are reserved and cannot be overridden. Common variables include `FLUX_LOG_LEVEL`, `FLUX_REGION`, and `FLUX_FEATURE_FLAGS`. Variables can reference other variables using `${VAR_NAME}` syntax, resolved at deployment time. Variable changes take effect on the next deployment — they do not hot-reload into running containers.

## Environment Promotion

Promotion copies configuration from one environment to another. The typical flow is development to staging to production. Promote via `POST /v2/environments/{source}/promote` with the `target` environment name. Promotion copies environment variables, feature flags, and scaling configuration. It does NOT copy secrets (for security), database contents, or deployment artifacts. After promotion, review the diff at `GET /v2/environments/{target}/pending-changes` before deploying. You can also promote selectively by specifying a `variables` array to include only specific settings. Promotion creates an audit entry with the source, target, actor, and timestamp. Roll back a promotion via `POST /v2/environments/{target}/rollback` which restores the previous configuration snapshot.

## Environment Isolation

Each environment is fully isolated at the infrastructure level. Separate compute instances, network policies, and data stores ensure that development activity cannot affect production. Cross-environment access is blocked by default. Enable explicit cross-environment read access via environment linking under **Settings > Environment Links** for specific use cases like production data sampling.
