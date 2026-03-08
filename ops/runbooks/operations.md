# Runbook: Rate-Limit Tightening

## Symptoms
- `robots.txt` compliance alerts firing
- Upstream OEM site returning 429 or 503 errors
- Crawl job durations increasing

## Immediate Actions

1. Check current crawl delay:
   ```bash
   vmw crawl status
   ```

2. Stop active crawls if 429s are occurring:
   ```bash
   vmw crawl stop <crawl_id>
   ```

3. Increase crawl delay for the affected adapter in the sources table:
   ```sql
   UPDATE sources SET crawl_delay = 10.0 WHERE adapter = 'adapter_id';
   ```

4. Wait 30 minutes and restart with reduced concurrency:
   ```bash
   vmw crawl start <source_id>
   ```

## Permanent Fix
- Update adapter's `crawl_delay` class attribute
- Add per-IP proxy rotation if needed
- Review robots.txt for updated `Crawl-delay` directive

---

# Runbook: Parser Breakage

## Symptoms
- `parse_status = 'failed'` documents accumulating
- `ParseLatencyHigh` or parse error alerts firing

## Diagnosis
```bash
# Check recent parse failures
psql $VMW_PG_DSN -c "SELECT content_id, metadata->>'error' FROM documents WHERE parse_status='failed' LIMIT 20;"
```

## Fix
1. Identify failing document type (PDF vs HTML)
2. If PyMuPDF fails, check if pdfminer fallback also fails → may need qpdf repair
3. Re-queue failed docs:
   ```bash
   vmw parse reprocess --since 2024-01-01T00:00:00
   ```

---

# Runbook: OpenSearch Reindex

## When to Use
- Mapping change requiring full reindex
- Index corruption detected

## Steps
1. Create new index with updated mapping:
   ```bash
   vmw index rebuild --scope manuals
   ```
2. Monitor index lag metric in Grafana
3. Switch alias to new index when caught up

---

# Runbook: Disaster Recovery

## S3/MinIO
- All blobs are content-addressed — no ordering dependency
- Restore from CRR (Cross-Region Replication) bucket in secondary region
- S3 Versioning retains all blob versions

## Postgres
- Automated RDS snapshots (7-day retention)
- Restore: `aws rds restore-db-instance-from-db-snapshot`
- Run migrations: `alembic upgrade head`

## OpenSearch
- Reindex from Postgres + S3 blobs:
  ```bash
  vmw index rebuild --scope all
  ```

## Full Stack Recovery Checklist
- [ ] Restore Postgres from snapshot
- [ ] Verify S3 blobs accessible
- [ ] Run `alembic upgrade head`
- [ ] Rebuild OpenSearch indexes
- [ ] Verify API health: `curl /health`
- [ ] Run smoke tests: `make smoke`
