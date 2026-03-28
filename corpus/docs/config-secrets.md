# FluxAPI Secret Management

FluxAPI provides a built-in secrets manager for storing sensitive configuration values. Secrets are encrypted at rest and in transit, with fine-grained access controls and full audit logging.

## Storing Secrets

Create secrets via `POST /v2/secrets` with `name`, `value`, and optional `environment` fields. Secret names follow the pattern `[a-z][a-z0-9-]*` (lowercase with hyphens). If no environment is specified, the secret is available in all environments. Secret values are encrypted using AES-256-GCM with environment-specific encryption keys. Maximum value size is 64KB. Secrets are never returned in plaintext via the API after creation — only the secret metadata (name, created_at, version) is readable. To use a secret in your application, reference it as `$SECRET{secret-name}` in environment variables or configuration files. The FluxAPI runtime injects the decrypted value at container startup.

## Vault Integration

For enterprise customers, FluxAPI integrates with external vault services including HashiCorp Vault, AWS Secrets Manager, and Azure Key Vault. Configure vault integration under **Settings > Secrets > External Vault**. Once connected, FluxAPI can sync secrets bidirectionally. External vault secrets are referenced as `$VAULT{path/to/secret}`. Vault integration supports automatic lease renewal and dynamic credentials. Connection to the external vault uses mTLS with certificates managed by FluxAPI. Vault failover: if the external vault is unreachable, FluxAPI falls back to the last cached values for up to 1 hour, after which container restarts will fail until vault connectivity is restored.

## Secret Rotation Policies

Automate secret rotation with rotation policies. Create a policy via `POST /v2/secrets/{name}/rotation-policy` with `interval` (in days), `generator` (the rotation strategy), and optional `notification_channels`. Built-in generators include `random-string` (configurable length and character set), `rsa-keypair` (2048 or 4096 bit), and `database-password` (generates and updates the associated database credential). Custom generators can call a webhook URL that returns the new secret value. When rotation occurs: (1) the new value is generated, (2) a new secret version is created, (3) the old version remains accessible for the grace period (default 24 hours), (4) running containers receive the new value on their next restart or via hot-reload if enabled, (5) the old version is marked as deprecated after the grace period. View rotation history via `GET /v2/secrets/{name}/versions`.

## Access Control

Secret access is controlled by IAM policies. By default, only project admins can create and manage secrets. Grant read access to specific secrets via `POST /v2/secrets/{name}/access` with the principal (user, service account, or role). Audit all secret access events via `GET /v2/audit/secrets` which logs every read, write, rotation, and access grant with timestamps and actor identity.
