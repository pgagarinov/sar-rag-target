# FluxAPI Authentication: API Keys

API keys are the simplest way to authenticate with FluxAPI. Every request to the FluxAPI platform must include a valid API key in the `X-Flux-Key` header. Keys are tied to a specific project and carry scoped permissions.

## Creating API Keys

To create a new API key, navigate to the FluxAPI Dashboard under **Settings > API Keys** and click "Generate New Key". You must assign each key a descriptive label and select the permission scope. Available scopes include `read`, `write`, `admin`, and `billing`. Keys are shown only once at creation time — store them securely. You can create up to 50 keys per project. Each key is a 64-character hexadecimal string prefixed with `flx_`. Keys can also be created programmatically via `POST /v2/api-keys` with the required `scope` and `label` fields in the request body. The response includes the key value and unique key ID.

## Key Rotation

To rotate an API key without downtime, use the key rotation endpoint `POST /v2/api-keys/{key_id}/rotate`. This creates a new key with the same scopes and permissions while keeping the old key active for a configurable grace period. The default grace period is 24 hours, configurable up to 7 days via the `grace_period` parameter. During the grace period, both old and new keys are valid. After the grace period expires, the old key is automatically revoked. Best practices for zero-downtime rotation: (1) call the rotate endpoint to generate a new key, (2) update your application configuration with the new key value, (3) deploy the configuration change across all services, (4) verify requests succeed with the new key, (5) optionally revoke the old key early via `DELETE /v2/api-keys/{old_key_id}`. The rotation endpoint returns both the new key value and a rotation ID for tracking in the audit log. Automated rotation can be scheduled via the dashboard or programmatically via `PUT /v2/api-keys/{key_id}/auto-rotate` with a cron expression.

## Rate Limits Per Key

Each API key has independent rate limits. The default is 1000 requests per minute for read-scoped keys, 200 for write-scoped keys, and 100 for admin keys. Request increases through the dashboard under **Settings > Rate Limits**. When a key exceeds its limit, the API returns HTTP 429 with a `Retry-After` header. Rate limits reset on a rolling window basis. Monitor usage via `GET /v2/usage/rate-limits`.

## Key Revocation and Audit

Revoke a key immediately via `DELETE /v2/api-keys/{key_id}`. Revoked keys return HTTP 401. All key lifecycle events are logged in the audit trail at `GET /v2/audit/api-keys`.
