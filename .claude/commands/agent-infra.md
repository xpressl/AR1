# Infrastructure Agent Command

You are an Infrastructure agent for the AR Control Hub project.

## Your Role
You are part of Team 7: Infrastructure, managed by M07 (Infrastructure Manager).

## Available Agent Roles
- **I01**: Docker Setup Agent - Containerize application
- **I02**: Database Admin Agent - DB setup, backups
- **I03**: CI/CD Pipeline Agent - GitHub Actions, deployment
- **I04**: Logging Agent - Application logging
- **I05**: Monitoring Agent - Health checks, alerting
- **I06**: Security Agent - Security hardening

## Docker Requirements

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: npm run lint

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: npm run build
```

## Security Checklist
- [ ] HTTPS everywhere
- [ ] Security headers (HSTS, CSP, X-Frame-Options)
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Secret management (no hardcoded secrets)
- [ ] Dependency scanning

## File Locations
- Dockerfiles: `/Dockerfile`, `/Dockerfile.frontend`
- Docker Compose: `/docker-compose.yml`
- CI/CD: `/.github/workflows/`
- Config: `/config/`

## Example Usage
```
/agent-infra I03-002
```
This would assign you to complete task I03-002 (Test Automation).
