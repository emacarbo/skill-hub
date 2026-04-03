---
name: migration-architect
description: Use when planning zero-downtime migrations -- database schema evolution, service cutover, data validation, rollback strategies. Covers expand-contract, strangler fig, canary, and CDC patterns.
---

# Migration Architect

Zero-downtime migration planning, compatibility validation, and rollback strategy generation.

## Database Migration Patterns

### Expand-Contract Pattern
1. **Expand:** Add new columns/tables alongside existing schema
2. **Dual Write:** App writes to both old and new schema
3. **Migration:** Backfill historical data
4. **Contract:** Remove old columns/tables after validation

### Parallel Schema Pattern
- Run new schema alongside existing
- Feature flags route traffic between schemas
- Validate data consistency between systems
- Cutover when confidence is high

### Change Data Capture (CDC)
- Stream database changes to target system
- Maintain eventual consistency during migration
- Enables zero-downtime for large datasets

### Data Migration Strategies
- **Snapshot:** Full data copy during maintenance window
- **Incremental Sync:** Continuous sync with change tracking
- **Dual-Write:** Write to both systems; compensation for failures

## Service Migration Patterns

### Strangler Fig
1. Route traffic through proxy/gateway
2. Implement new service incrementally
3. Retire legacy components as new ones prove stable
4. Monitor performance and error rates throughout

### Canary Deployment
1. Deploy to small percentage of users
2. Monitor latency, errors, business KPIs
3. Gradually increase traffic percentage
4. Full rollout once validation passes

### Parallel Run
- Dual execution with shadow traffic
- Compare outputs to validate correctness
- Gradual cutover based on confidence

## Feature Flags for Migrations

```python
class MigrationFeatureFlag:
    def __init__(self, flag_name, rollout_percentage=0):
        self.flag_name = flag_name
        self.rollout_percentage = rollout_percentage

    def is_enabled_for_user(self, user_id):
        return (hash(f"{self.flag_name}:{user_id}") % 100) < self.rollout_percentage
```

## Circuit Breaker Pattern

```python
class MigrationCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call_new_service(self, request):
        if self.state == 'OPEN':
            if self.should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                return self.fallback_to_legacy(request)
        try:
            response = self.new_service.process(request)
            self.on_success()
            return response
        except Exception:
            self.on_failure()
            return self.fallback_to_legacy(request)
```

## Data Validation

### Validation Strategies
1. **Row Count:** Compare counts between source/target (account for soft deletes)
2. **Checksums:** Generate hashes for critical data subsets; sampling for large sets
3. **Business Logic:** Run critical queries on both systems, compare aggregates

### Delta Reconciliation

```sql
SELECT 'missing_in_target' as issue, source_id FROM source_table s
WHERE NOT EXISTS (SELECT 1 FROM target_table t WHERE t.id = s.id)
UNION ALL
SELECT 'extra_in_target', target_id FROM target_table t
WHERE NOT EXISTS (SELECT 1 FROM source_table s WHERE s.id = t.id);
```

## Rollback Strategies

### Database Rollback
- Schema version control with rollback scripts per step
- Point-in-time recovery via backups
- Data snapshots at migration checkpoints

### Service Rollback
- **Blue-Green:** Keep previous version running; switch traffic back if needed
- **Rolling:** Gradually shift traffic back; monitor health during rollback

### Infrastructure Rollback
- Version-controlled IaC (Terraform/CloudFormation)
- Tested rollback templates in staging

## Risk Assessment

| Category | Key Risks |
|----------|-----------|
| **Technical** | Data loss/corruption, downtime, integration failures, scalability under load |
| **Business** | Revenue impact, customer experience, compliance, reputation |
| **Operational** | Knowledge gaps, insufficient testing, monitoring gaps |

### Mitigations
- Comprehensive testing (unit, integration, load, chaos)
- Gradual rollout with automated rollback triggers
- Data validation and reconciliation at each phase
- Stakeholder communication plans

## Migration Runbook

### Pre-Migration
- [ ] Plan reviewed and approved
- [ ] Rollback procedures tested
- [ ] Monitoring/alerting configured
- [ ] Backup and recovery verified
- [ ] Performance benchmarks established
- [ ] Security review completed

### During Migration
- [ ] Execute phases in order; monitor KPIs continuously
- [ ] Validate data at each checkpoint
- [ ] Rollback if success criteria not met
- [ ] Document deviations

### Post-Migration
- [ ] All success criteria met
- [ ] Data reconciliation complete
- [ ] Monitor 72 hours
- [ ] Decommission legacy (if applicable)
- [ ] Retrospective conducted

## CI/CD Integration

```yaml
migration_validation:
  stage: test
  script:
    - python scripts/compatibility_checker.py --before=old_schema.json --after=new_schema.json
    - python scripts/migration_planner.py --config=migration_config.json --validate
```

## Success Metrics

| Category | Metrics |
|----------|---------|
| **Technical** | Completion rate, downtime, data consistency score, performance delta, error rate |
| **Business** | Customer impact, revenue protection, time to value |
| **Operational** | Plan adherence, issue resolution time, knowledge transfer |
