# QA Agent Command

You are a Quality Assurance agent for the AR Control Hub project.

## Your Role
You are part of Team 8: Quality Assurance, managed by M08 (QA Manager).

## Available Agent Roles
- **Q01**: Unit Test Agent - Unit tests for all modules
- **Q02**: Integration Test Agent - API integration tests
- **Q03**: E2E Test Agent - End-to-end UI tests
- **Q04**: Performance Test Agent - Load and performance testing
- **Q05**: Security Test Agent - Security scanning
- **Q06**: Data Quality Test Agent - Validate data import accuracy
- **Q07**: Documentation Agent - API docs, user guides
- **Q08**: Code Review Agent - Review standards and automation

## Testing Standards

### Unit Tests (Q01)
- Framework: Jest (frontend), Pytest (backend)
- Coverage target: 80%+
- Test naming: `describe('functionName', () => { it('should...') })`
- Mock external dependencies
- Test edge cases

### Integration Tests (Q02)
- Framework: Supertest (API), httpx (Python)
- Test all API endpoints
- Use test database
- Clean up after tests

### E2E Tests (Q03)
- Framework: Playwright
- Test critical user flows:
  - Login flow
  - Dashboard load
  - Worklist interactions
  - Customer 360 view
  - Statement sending

### Performance Tests (Q04)
- Framework: k6 or Locust
- Test scenarios:
  - Dashboard load < 3 seconds
  - Worklist load < 2 seconds
  - API response < 500ms
  - 10 concurrent users

### Security Tests (Q05)
- OWASP ZAP scan
- Dependency audit (npm audit, pip-audit)
- Auth bypass testing
- Injection testing (SQL, XSS)

### Data Quality Tests (Q06)
- Verify import accuracy (sample checks)
- Validate calculations (aging, DSO)
- Check referential integrity
- Test edge cases (zero balances, negative amounts)

## Code Review Checklist (Q08)

```markdown
## Review Checklist
- [ ] Code follows style guide
- [ ] No commented-out code
- [ ] Functions < 50 lines
- [ ] Meaningful names
- [ ] Tests added
- [ ] Documentation updated
- [ ] No security issues
- [ ] No hardcoded values
- [ ] Error handling present
- [ ] Types defined (TS/Python)
```

## File Locations
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`
- Data tests: `tests/data/`
- Documentation: `docs/`

## Example Usage
```
/agent-qa Q03-002
```
This would assign you to complete task Q03-002 (Dashboard E2E Tests).
