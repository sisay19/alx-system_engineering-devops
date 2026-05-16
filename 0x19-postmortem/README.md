# Postmortem: Payment Service Outage – August 12, 2024

## Issue Summary

- **Duration**  
  Start: 2024-08-12 09:15 UTC  
  End: 2024-08-12 11:42 UTC  
  **Total outage: 2 hours 27 minutes**

- **Impact**  
  The payment checkout service returned HTTP 500 errors for 100% of transactions.  
  Users were unable to complete purchases. Approximately **68% of all active users** (those trying to pay) were affected.  
  No data loss occurred, but the company lost an estimated $340k in sales.

- **Root Cause**  
  A recently deployed code change added a new payment gateway integration, but an environment variable (`NEW_GATEWAY_API_KEY`) was missing in production.  
  The service crashed on startup because it treated a missing key as an unrecoverable error.

## Timeline (all times UTC)

- **09:15** – Incident begins: error rate spikes to 100% on the checkout endpoint.  
- **09:18** – Detected by automated monitoring (Prometheus + Alertmanager) sending a “High 5xx Rate” critical alert to the on-call SRE.  
- **09:20** – On-call engineer checks service logs and sees “Failed to initialize gateway: missing API key”.  
- **09:25** – Engineer assumes the gateway vendor changed their API schema (misleading path).  
- **09:35** – Escalated to the backend team lead.  
- **09:50** – Team lead suspects a network policy blocking outbound traffic to the new gateway – spends 30 minutes checking firewall rules (dead end).  
- **10:25** – Incident escalated to the DevOps team.  
- **10:40** – DevOps compares configuration files between staging (working) and production – notices missing environment variable.  
- **11:00** – Hotfix deployed to add `NEW_GATEWAY_API_KEY` via secret manager.  
- **11:05** – Service restarts; error rate starts dropping.  
- **11:42** – All systems nominal; 100% of payments successful. Monitoring closed.

## Root Cause and Resolution

**Root cause**  
The payment service’s initialization code required the `NEW_GATEWAY_API_KEY` environment variable to exist.  
If absent, the service would panic and crash (Go’s `log.Fatal`).  
The variable was correctly defined in staging and development but **missed in the production secret store** due to a human error in a deployment script.

**Resolution**  
The missing environment variable was added to the production secret manager (AWS Secrets Manager).  
The service was restarted, and the new gateway client initialized correctly. No code rollback was required.

## Corrective and Preventative Measures

- **Improvements**  
  - Make missing configuration **non‑fatal** (graceful degradation or fallback to old gateway).  
  - Automatically compare environment variables between staging and production before deployment.  
  - Add startup readiness probe that fails only after a clear error message, but keeps service running in “degraded” mode.

- **Specific TODO tasks**  
  - [ ] Patch code: Change `log.Fatal` to `log.Error` + disable new gateway only (keep old gateway active).  
  - [ ] Add monitoring: Alert on missing required environment variables at startup.  
  - [ ] Automate validation: Extend CI/CD to block deployment if any production variable is missing compared to staging.  
  - [ ] Runbook entry: Document “missing API key” symptom and fix in the team’s playbook.  
  - [ ] Post‑deployment test: Add a smoke test that verifies both gateways can initialize before declaring a deployment healthy.
