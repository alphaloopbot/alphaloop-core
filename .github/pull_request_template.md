## Description

Brief description of changes made in this PR.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Infrastructure package update
- [ ] Service enhancement
- [ ] Database schema change
- [ ] Docker configuration update

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules

## AlphaLoop-Specific Testing

- [ ] Infrastructure packages tests pass: `make test-all`
- [ ] Core functionality tests pass: `poetry run pytest tests/unit/ -v`
- [ ] Linting passes: `make lint`
- [ ] Type checking passes: `make type-check`
- [ ] Database setup works: `make database-setup`
- [ ] Services build successfully: `make services-build`
- [ ] E2E tests pass (if applicable): `make database-test`
- [ ] Docker containers start correctly: `make services-start`

## Infrastructure Package Changes

If this PR affects infrastructure packages, please check:

- [ ] `alphaloop-logging` functionality tested
- [ ] `alphaloop-security` functionality tested
- [ ] `alphaloop-storage` functionality tested
- [ ] `alphaloop-cache` functionality tested
- [ ] `alphaloop-heartbeat` functionality tested
- [ ] Service factory updated (if needed)
- [ ] Configuration files updated (if needed)

## Service Changes

If this PR affects services, please check:

- [ ] System metrics service functionality verified
- [ ] Market data service functionality verified
- [ ] Database connectivity tested
- [ ] Data collection verified
- [ ] Service health checks working
- [ ] Docker health checks passing

## Documentation

- [ ] README.md updated (if needed)
- [ ] CHANGELOG.md updated with new entries under [Unreleased]
- [ ] Architecture diagrams updated (if applicable)
- [ ] ADR documents updated (if applicable)
- [ ] Infrastructure package READMEs updated (if applicable)
- [ ] API documentation updated (if applicable)

## Database Changes

If this PR includes database changes:

- [ ] `config/database_schema.yaml` updated
- [ ] Schema changes follow single source of truth principle
- [ ] No hardcoded table definitions added
- [ ] Migration strategy documented
- [ ] Backward compatibility considered

## Docker & Deployment

If this PR affects Docker or deployment:

- [ ] Dockerfiles updated (if needed)
- [ ] Docker Compose files updated (if needed)
- [ ] Environment variables documented
- [ ] Health checks implemented
- [ ] Security considerations addressed (non-root user, etc.)

## Additional Notes

Any additional information that reviewers should know about this PR.

### Breaking Changes

If this PR includes breaking changes, please describe:
- What is breaking
- Migration steps required
- Impact on existing deployments

### Performance Impact

If this PR affects performance:
- Performance metrics before/after
- Resource usage changes
- Scalability considerations

### Security Considerations

If this PR affects security:
- Security implications
- Authentication/authorization changes
- Data encryption considerations
