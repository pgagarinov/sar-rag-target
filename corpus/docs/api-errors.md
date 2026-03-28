# FluxAPI Error Handling

FluxAPI uses standard HTTP status codes and a consistent error response format. Understanding error codes and implementing proper retry logic is essential for building resilient integrations.

## Error Response Format

All error responses follow a standard JSON structure with a top-level `error` object containing `code`, `message`, `details`, and `request_id` fields. The `code` field is a machine-readable string like `rate_limit_exceeded` or `resource_not_found`. The `message` field is a human-readable description. The `details` field is an optional array of specific validation errors or contextual information. The `request_id` field is a unique identifier for the request useful for support inquiries. Example error response: `{"error": {"code": "validation_failed", "message": "Request body contains invalid fields", "details": [{"field": "name", "issue": "must be between 3 and 64 characters"}], "request_id": "req_abc123"}}`.

## Client Error Codes (4xx)

HTTP 400 Bad Request: malformed JSON, missing required fields, or invalid field values. Check the `details` array for specific field-level errors. HTTP 401 Unauthorized: missing or invalid API key, expired OAuth token, or revoked credentials. Re-authenticate and retry. HTTP 403 Forbidden: valid credentials but insufficient permissions. Check the key scope or OAuth token scope. HTTP 404 Not Found: the resource does not exist or you lack permission to see it. FluxAPI returns 404 rather than 403 for resources outside your project to prevent enumeration. HTTP 409 Conflict: the resource state conflicts with the request, often due to concurrent modifications. Read the current state and retry with updated data. HTTP 422 Unprocessable Entity: syntactically valid request but semantically invalid. Common for business logic violations. HTTP 429 Too Many Requests: rate limit exceeded. Read the `Retry-After` header and wait before retrying. The `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers indicate your current quota status.

## Server Error Codes (5xx)

HTTP 500 Internal Server Error: unexpected failure. These are automatically reported to the FluxAPI engineering team. HTTP 502 Bad Gateway: upstream service temporarily unreachable. Retry after 5-10 seconds. HTTP 503 Service Unavailable: planned maintenance or capacity limits. Check `https://status.fluxapi.io` for incident status. HTTP 504 Gateway Timeout: upstream service did not respond in time. Retry with exponential backoff.

## Retry Guidance

For transient errors (429, 500, 502, 503, 504), implement exponential backoff with jitter. Start with a 1-second delay, double on each retry, add random jitter of 0-500ms, and cap at 60 seconds. Maximum 5 retries. For 429 errors specifically, respect the `Retry-After` header value. Do not retry 400, 401, 403, 404, or 422 errors — these require code changes, not retries.
