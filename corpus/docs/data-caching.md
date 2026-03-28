# FluxAPI Caching

FluxAPI provides managed caching layers to reduce latency and database load. The primary cache service is a managed Redis instance, with optional CDN caching for static assets and API response caching.

## Cache Architecture

FluxAPI caching operates at three layers. Layer 1: API response cache — FluxAPI automatically caches GET responses based on `Cache-Control` headers. Layer 2: Application cache — your code interacts with a managed Redis instance for custom key-value caching. Layer 3: CDN edge cache — static assets and marked API responses are cached at edge locations worldwide. Each layer can be configured independently. Disable any layer via environment variables: `FLUX_CACHE_API=false`, `FLUX_CACHE_REDIS=false`, `FLUX_CACHE_CDN=false`. Cache hit rates are visible in the dashboard under **Monitoring > Cache Performance**.

## Redis Integration

Every FluxAPI project includes a managed Redis instance (Redis 7+). Access Redis via the connection endpoint at `GET /v2/cache/connection` which returns the host, port, and auth token. The Redis instance supports all standard Redis commands and data structures. Default memory allocation is 256MB on starter plans, up to 64GB on enterprise plans. Connection to Redis uses TLS encryption. Maximum concurrent connections to Redis depends on the plan: 100 (starter), 500 (professional), 2000 (enterprise). Use the FluxAPI SDK's built-in cache client for automatic serialization and connection management: `flux.cache.get(key)`, `flux.cache.set(key, value, ttl=300)`. Redis connections are pooled by the SDK — the default Redis connection pool size is 10 per application instance.

## TTL Policies

Every cached value should have a TTL (time-to-live) to prevent stale data. Set TTL per key via the `ttl` parameter in seconds. Default TTL is 300 seconds (5 minutes) if not specified. Configure global TTL defaults per environment via `FLUX_CACHE_DEFAULT_TTL`. TTL strategies by data type: user session data (3600s), configuration values (1800s), API response cache (300s), computed aggregations (600s). For time-sensitive data, use shorter TTLs or implement active invalidation. The `EXPIRE` and `PEXPIRE` Redis commands allow adjusting TTL on existing keys. Keys without TTL are evicted using the `allkeys-lru` policy when memory is full.

## Cache Invalidation

Invalidate cached data when the underlying source changes. Strategies include: (1) TTL-based expiry — simplest, eventual consistency. (2) Active invalidation — call `flux.cache.delete(key)` or `DEL` on write operations. (3) Tag-based invalidation — tag related keys with `flux.cache.set(key, value, tags=["user:123"])` and invalidate all keys for a tag via `flux.cache.invalidate_tag("user:123")`. (4) Pub/sub invalidation — subscribe to change events and invalidate on notification. For multi-region deployments, invalidation propagates across regions within 500ms. Monitor stale hit rates via the cache dashboard.
