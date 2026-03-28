# FluxAPI Performance Troubleshooting

When your FluxAPI application experiences latency issues, slow responses, or degraded throughput, follow this systematic debugging guide to identify and resolve bottlenecks.

## Latency Debugging

Start by identifying where latency occurs. FluxAPI injects distributed tracing headers (`X-Flux-Trace-Id`) into every request. View trace details in the dashboard under **Monitoring > Traces**. Each trace shows the request lifecycle: load balancer ingress, container routing, application processing, and downstream calls. Common latency sources: (1) Cold starts — first request to a new container takes 1-5 seconds for initialization. Mitigate with minimum replicas > 0 and pre-warming endpoints. (2) DNS resolution — internal service discovery adds 1-2ms. Cache DNS results in your application. (3) TLS handshake — first connection to external services adds 50-100ms. Use connection pooling to reuse TLS sessions. (4) Downstream API calls — external service latency is often the largest component. Set timeouts and use circuit breakers.

## Profiling Tools

FluxAPI provides built-in profiling for CPU, memory, and I/O. Enable continuous profiling via `PUT /v2/deployments/{id}/profiling` with `enabled: true`. Profiling adds approximately 2-3% CPU overhead. View flame graphs in the dashboard under **Monitoring > Profiling**. For on-demand profiling, trigger a 30-second capture via `POST /v2/deployments/{id}/profile` which returns a downloadable profile file. CPU profiling identifies hot functions and unexpected computation. Memory profiling shows allocation patterns and potential leaks. I/O profiling reveals slow disk operations, network waits, and lock contention. Compare profiles across time periods to identify regressions.

## Common Bottlenecks

Database queries are the most frequent bottleneck. Check slow query logs via `GET /v2/databases/{id}/slow-queries` (queries exceeding 100ms). Add indexes for frequently filtered columns. Use `EXPLAIN ANALYZE` to understand query plans. Connection pool exhaustion causes requests to queue — monitor pool stats and increase size if needed. Memory pressure triggers garbage collection pauses. Monitor memory usage and right-size your container plan. Event loop blocking (Node.js) or GIL contention (Python) limits throughput for CPU-bound workloads — offload heavy computation to worker queues. Cache miss storms occur when cache TTL expires simultaneously for many keys — use jittered TTL values.

## Performance Optimization Checklist

Follow this checklist to systematically improve performance: (1) Enable caching for repeated queries and API calls. (2) Use connection pooling for databases and external services. (3) Set appropriate timeouts on all downstream calls (recommend 5s default). (4) Implement circuit breakers for non-critical dependencies. (5) Right-size container resources based on profiling data. (6) Use async/non-blocking I/O where possible. (7) Batch database operations instead of N+1 queries. (8) Enable HTTP/2 for multiplexed connections. (9) Compress response payloads with gzip/brotli. (10) Monitor and alert on P95/P99 latency, not just averages. Configure performance alerts via `POST /v2/alerts` with metric-based triggers.
