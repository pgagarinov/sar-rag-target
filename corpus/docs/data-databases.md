# FluxAPI Managed Databases

FluxAPI provides fully managed database instances with automated backups, scaling, and monitoring. Supported engines include PostgreSQL 15+, MySQL 8+, and MongoDB 7+.

## Provisioning and Connection

Create a managed database via `POST /v2/databases` with `engine`, `version`, `plan`, and `region` fields. Available plans range from `starter` (1 vCPU, 1GB RAM, 10GB storage) to `enterprise` (32 vCPU, 128GB RAM, 2TB storage). Provisioning takes 2-5 minutes. Connection strings are generated per environment and available via `GET /v2/databases/{id}/connection`. Connection strings include the host, port, database name, and credentials. Store the connection string as a secret using the FluxAPI secrets manager — never hardcode it. TLS is enforced for all connections. Each database instance supports up to 500 concurrent connections depending on the plan. Connection details include a read-write endpoint and, for plans with replicas, a read-only endpoint.

## Connection Pooling

FluxAPI includes built-in connection pooling via PgBouncer (PostgreSQL) or ProxySQL (MySQL). Connection pooling reduces database load by reusing connections across requests. The default pool size is 25 connections per application instance, configurable via the `FLUX_DB_POOL_SIZE` environment variable. Pool mode is `transaction` by default — connections are returned to the pool after each transaction completes. Alternative modes include `session` (connection held for the entire client session) and `statement` (returned after each statement). Monitor pool utilization via `GET /v2/databases/{id}/pool-stats` which returns active, idle, and waiting connection counts. If your application sees `connection pool exhausted` errors, either increase the pool size, optimize query duration, or upgrade the database plan.

## Migrations

FluxAPI tracks database schema migrations automatically. Create migrations via the CLI: `flux db migrate create <name>`. Migration files are stored in `migrations/` in your project repository. Apply migrations during deployment via the `pre_deploy` hook or manually via `POST /v2/databases/{id}/migrate`. Migrations run inside a transaction — if any step fails, the entire migration is rolled back. View migration status via `GET /v2/databases/{id}/migrations` which lists applied and pending migrations. Rollback the last migration via `POST /v2/databases/{id}/migrate/rollback`. Never modify a migration file after it has been applied — create a new migration instead.

## Backups and Recovery

Automated backups run daily at the configured backup window (default 02:00-03:00 UTC). Backups are retained for 30 days on paid plans and 7 days on starter plans. Point-in-time recovery (PITR) is available for PostgreSQL and MySQL, allowing restore to any second within the retention window. Trigger a manual backup via `POST /v2/databases/{id}/backups`. Restore from backup via `POST /v2/databases/{id}/restore` with the `backup_id` or a `target_time` for PITR. Restores create a new database instance — the original remains untouched.
