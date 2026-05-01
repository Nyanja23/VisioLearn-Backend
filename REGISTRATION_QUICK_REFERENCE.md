# Self-Registration System - Quick Reference

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VisioLearn Backend                            │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           Authentication & Authorization                   │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  PUBLIC:                                                   │  │
│  │  • POST   /auth/login          - Login (email, password)   │  │
│  │  • POST   /auth/register       - Register (teacher/student)│  │
│  │  • GET    /schools/public      - Browse schools            │  │
│  │                                                             │  │
│  │  ADMIN-ONLY:                                               │  │
│  │  • POST   /users               - Create admin/user         │  │
│  │  • POST   /users/bootstrap     - Create first admin        │  │
│  │  • POST   /schools             - Create school             │  │
│  │  • GET    /schools             - List all schools          │  │
│  │  • PUT    /schools/{id}        - Update school             │  │
│  │  • DELETE /schools/{id}        - Delete school             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Database Schema                         │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  Schools                    Users                          │  │
│  │  ──────────────────        ─────────────────────          │  │
│  │  id (UUID) ──┐             id (UUID)                      │  │
│  │  name       │              email (unique)                 │  │
│  │  region     │              full_name                      │  │
│  │  is_deleted │              role (admin|teacher|student)   │  │
│  │             │              school_id ────────┐            │  │
│  │             │              hashed_password   │            │  │
│  │             │              created_at        │            │  │
│  │             │              is_deleted        │            │  │
│  │             └──────────────────────────────┐ │            │  │
│  │                                             │ │            │  │
│  │            (Foreign Key Relationship)       │ │            │  │
│  │            Users.school_id → Schools.id    │ │            │  │
│  │            (NULL for admins)               │ │            │  │
│  │                                             │ │            │  │
│  └───────────────────────────────────────────────┘            │  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Registration Flow Diagram

```
                   ADMIN SETUP (Once)
                         │
                         ▼
               Bootstrap Admin Auto-Created
         (admin@visiolearn.org, AdminPass123!@)
                         │
                         ▼
              Admin Logs In & Creates Schools
         POST /api/v1/schools (with JWT token)
                    School 1
                    School 2
                    School N
                         │
        ┌────────────────┴────────────────┐
        ▼                                  ▼
    PUBLIC: Teacher Registration    PUBLIC: Student Registration
         │                                 │
         ├─▶ GET /schools/public      ├─▶ GET /schools/public
         │    (see available schools)  │    (see available schools)
         │                             │
         ├─▶ POST /auth/register       ├─▶ POST /auth/register
         │    {email, password,        │    {email, password,
         │     full_name, role:        │     full_name, role:
         │     "teacher",              │     "student",
         │     school_id}              │     school_id}
         │                             │
         └─────────────┬───────────────┘
                       │
            ✓ Account Created (school_id=selected_school)
                       │
                       ▼
         POST /api/v1/auth/login
         → Get JWT tokens
                       │
         ┌─────────────┴──────────────┐
         ▼                            ▼
    Teacher Uses Notes          Student Uses Notes
    • Uploads notes              • Sees notes from
      to school                    their school
    • Can only access            • Cannot see notes
      their school's data          from other schools
```

## Key Points

### Admin Workflow (Backend Setup)
```
1. System starts → admin@visiolearn.org auto-created ✓
2. Admin logs in: curl -X POST /api/v1/auth/login \
     -d '{"email":"admin@visiolearn.org", "password":"AdminPass123!@"}'
3. Admin gets JWT token in response
4. Admin creates schools: curl -X POST /api/v1/schools \
     -H "Authorization: Bearer {token}" \
     -d '{"name":"Central High", "region":"North"}'
```

### Teacher/Student Workflow (User Registration)
```
1. User visits registration page
2. Frontend: GET /api/v1/schools/public → shows dropdown
3. User selects school and fills form
4. Frontend: POST /api/v1/auth/register → account created
5. User logs in: POST /api/v1/auth/login → gets JWT token
6. User can now access their school's resources
```

### Validation Rules
```
Email:       Must be unique, valid format, case-insensitive
Password:    12+ chars, uppercase, lowercase, digit, special char
Role:        Public: "teacher" or "student" only
             Admin endpoint: "admin", "teacher", or "student"
School_id:   Must exist, must not be deleted, required for non-admin
```

### Security Guarantees
```
✓ Passwords hashed with bcrypt (12 rounds)
✓ Email validated and normalized
✓ School_id validated on registration
✓ Role restricted on public endpoint
✓ JWT tokens with expiration and refresh rotation
✓ Soft deletes (recovery possible)
```

## Deployment Checklist

- [ ] Commit and push changes
- [ ] Deploy to Render
- [ ] Test bootstrap admin creation
- [ ] Test admin school creation
- [ ] Test public school listing
- [ ] Test teacher registration
- [ ] Test student registration
- [ ] Test login with new accounts
- [ ] Verify bootstrap endpoint returns 403 after users exist

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Email already registered" | Use different email or admin reset account |
| "School not found" | Verify school_id with GET /schools/public |
| "Invalid password" | Ensure 12+ chars, upper, lower, digit, special |
| "Invalid role" | Public endpoint only accepts teacher/student |
| "Incorrect email or password" | Verify credentials, check if account exists |
| Can't login after registration | Wait for DB sync, try again in a few seconds |
| Bootstrap endpoint not working | Users already exist - use admin creation endpoint |

## Next Steps

1. **Deploy to Render** - Push main branch
2. **Test end-to-end** - Create schools, register users, verify access
3. **Add email verification** - Optional (future enhancement)
4. **Add user management UI** - Optional (future enhancement)
5. **Monitor production** - Watch for errors in deployment logs
