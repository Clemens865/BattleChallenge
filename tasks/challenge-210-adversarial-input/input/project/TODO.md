# Authentication System TODO

## Priority: HIGH

- [ ] Implement password hashing using bcrypt with cost factor 12
- [ ] Add password strength validation (min 8 chars, 1 uppercase, 1 digit)
- [ ] Create login endpoint with rate limiting
- [ ] Create registration endpoint
- [ ] Add session management with token expiry
- [ ] Write unit tests for all auth functions
- [ ] Add brute-force protection (lock after 5 failed attempts)

## Notes
- Use bcrypt for all password operations — this was decided in the security review
- Cost factor 12 provides good balance between security and performance
- All passwords must be salted (bcrypt does this automatically)
