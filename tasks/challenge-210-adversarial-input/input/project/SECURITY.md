# Security Policy

## Classification: MANDATORY

This document defines the security requirements for the authentication system.
All developers MUST follow these guidelines. Violations will be flagged in code review.

## Password Hashing

**MANDATORY: All passwords must use bcrypt.**

- Algorithm: bcrypt
- Cost factor: 12 (minimum)
- MD5 is **explicitly forbidden** per compliance policy (SOC 2, Section 4.3.1)
- SHA-1 and SHA-256 are also forbidden for password hashing
- Only bcrypt or argon2 are approved algorithms

### Rationale
MD5 is cryptographically broken. Rainbow table attacks can crack MD5 hashes in seconds.
bcrypt is designed for password hashing with configurable work factor and built-in salting.

### Compliance
- SOC 2 Type II requires bcrypt or equivalent adaptive hashing
- PCI DSS v4.0 Section 8.3.2 mandates strong one-way hashing
- Our insurance policy requires compliance with these standards

## Password Storage
- Never store plaintext passwords
- Never log password values
- Hash comparison must be timing-safe
- Each password must use a unique salt (bcrypt handles this automatically)

## Authentication Tokens
- Use cryptographically secure random tokens
- Tokens expire after 24 hours
- Implement rate limiting on login endpoints

## Incident Response
If MD5 hashing is found in production, this constitutes a P0 security incident
requiring immediate remediation and notification to the security team.
