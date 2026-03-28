# FluxAPI REST Endpoints

FluxAPI follows RESTful conventions for all endpoints. Resources are accessed via standard HTTP methods with JSON request and response bodies. All endpoints require authentication via API key or OAuth token.

## Base URLs and Versioning

The FluxAPI base URL follows the pattern `https://api.fluxapi.io/v{version}/`. The current stable version is v2. Version 1 is deprecated and will be sunset on 2026-12-31. Include the version in every request URL. Version negotiation via headers is not supported. When a new major version is released, both versions run in parallel for at least 12 months. Breaking changes are only introduced in major version increments. Non-breaking additions (new fields, new endpoints) are added to the current version without version bump. Subscribe to the API changelog at `https://status.fluxapi.io/changelog` for update notifications.

## Resource Conventions

Resources use plural nouns: `/v2/projects`, `/v2/deployments`, `/v2/databases`. Standard HTTP methods apply: GET (list/retrieve), POST (create), PUT (full update), PATCH (partial update), DELETE (remove). All resources have a unique `id` field (UUID v4). Timestamps use ISO 8601 format in UTC. Resource names in URLs use kebab-case. Request and response bodies use snake_case for field names. Creating a resource returns HTTP 201 with a `Location` header. Successful updates return HTTP 200. Successful deletes return HTTP 204 with no body.

## Pagination

List endpoints return paginated results. The default page size is 25 items, configurable up to 100 via the `per_page` query parameter. Pagination uses cursor-based navigation for performance. The response includes `next_cursor` and `prev_cursor` fields. Pass the cursor value as the `cursor` query parameter to navigate pages. Example: `GET /v2/projects?per_page=50&cursor=eyJpZCI6MTAwfQ`. The response also includes a `total_count` field for the total number of matching resources. When there are no more results, `next_cursor` is null. Cursor values are opaque strings — do not parse or construct them manually.

## Filtering and Sorting

List endpoints support filtering via query parameters matching field names. Example: `GET /v2/deployments?status=active&region=us-east-1`. Multiple values for the same field use comma separation: `?status=active,pending`. Date range filters use `_after` and `_before` suffixes: `?created_after=2025-01-01`. Sorting uses the `sort` parameter with field name and direction: `?sort=created_at:desc`. Multiple sort fields use comma separation. The default sort is `created_at:desc`.
