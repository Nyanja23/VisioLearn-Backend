# VisioLearn Self-Registration System

## Overview

The VisioLearn backend now supports **self-registration** for teachers and students. This eliminates the need for admins to manually create every account in the system.

## Architecture

### Three-Tier User Hierarchy

```
Admin (System Administrator)
  └── Created via: Bootstrap endpoint (first user only) or admin-only endpoint
      Cannot self-register
      Has system-wide permissions
      school_id = NULL (not scoped to any school)

School (Created by Admin)
  └── Created via: POST /api/v1/schools (admin-only)
      Contains name and region
      Can have multiple teachers and students

Teachers & Students (Self-Registration)
  └── Created via: POST /api/v1/auth/register (public)
      Must select a school during registration
      Can only access resources from their assigned school
      school_id = required (foreign key to Schools table)
```

## User Registration Workflow

### Phase 1: Admin Setup
1. System initializes with bootstrap admin (auto-created on first startup)
   - Email: `admin@visiolearn.org`
   - Password: `AdminPass123!@`

### Phase 2: School Creation
1. Admin logs in via `POST /api/v1/auth/login`
2. Admin creates schools via `POST /api/v1/schools`
   - Request body: `{ "name": "School Name", "region": "Region" }`
   - Response includes school `id` (UUID)

### Phase 3: Teachers Register
1. Teacher browses available schools via `GET /api/v1/schools/public` (no auth required)
   - Returns: `id`, `name`, `region` for all active schools
2. Teacher registers via `POST /api/v1/auth/register`
   - Required: `email`, `full_name`, `password`, `role=teacher`, `school_id`
   - Returns: User object with new teacher details

### Phase 4: Students Register
- Same process as teachers
- Use `role=student` instead of `role=teacher`

### Phase 5: Usage
1. Teacher logs in and uploads lesson notes
   - App automatically associates notes with teacher's school
   - Students can only see notes from their school
2. Student logs in and accesses notes from their school

## API Endpoints

### Public Endpoints (No Auth Required)

#### 1. List Active Schools for Registration
```http
GET /api/v1/schools/public?skip=0&limit=100

Response:
{
  "schools": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Central High School",
      "region": "North Region"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

#### 2. Register New Teacher/Student
```http
POST /api/v1/auth/register

Request:
{
  "email": "teacher@example.com",
  "full_name": "John Teacher",
  "password": "SecurePass123!@",
  "role": "teacher",  # or "student"
  "school_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response (201 Created):
{
  "id": "uuid-of-new-user",
  "email": "teacher@example.com",
  "full_name": "John Teacher",
  "role": "teacher",
  "school_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-05-01T14:30:00",
  "is_deleted": false
}

Error Cases:
- 400: Email already registered
- 400: School not found or deactivated
- 422: Invalid password strength
- 422: Invalid role (only teacher/student allowed)
```

### Authenticated Endpoints

#### 3. Login
```http
POST /api/v1/auth/login

Request:
{
  "email": "teacher@example.com",
  "password": "SecurePass123!@"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Admin-Only Endpoints

#### 4. Create School
```http
POST /api/v1/schools
Authorization: Bearer {admin_token}

Request:
{
  "name": "New School",
  "region": "South Region"
}

Response (201):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "New School",
  "region": "South Region",
  "created_at": "2025-05-01T14:30:00",
  "updated_at": "2025-05-01T14:30:00",
  "is_deleted": false
}
```

#### 5. Create Other Admins
```http
POST /api/v1/users
Authorization: Bearer {admin_token}

Request:
{
  "email": "otheradmin@example.com",
  "full_name": "Other Admin",
  "password": "AdminPass123!@",
  "role": "admin",
  "school_id": null  # Admins are not scoped to schools
}

Response (201):
{
  "id": "uuid-of-new-admin",
  "email": "otheradmin@example.com",
  "full_name": "Other Admin",
  "role": "admin",
  "school_id": null,
  "created_at": "2025-05-01T14:30:00",
  "is_deleted": false
}
```

#### 6. List Schools (Admin View)
```http
GET /api/v1/schools?skip=0&limit=10
Authorization: Bearer {admin_token}

Response:
{
  "schools": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Central High School",
      "region": "North Region",
      "created_at": "2025-05-01T14:30:00",
      "updated_at": "2025-05-01T14:30:00",
      "is_deleted": false
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

#### 7. Update School
```http
PUT /api/v1/schools/{school_id}
Authorization: Bearer {admin_token}

Request:
{
  "name": "Updated School Name",
  "region": "Updated Region"
}

Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated School Name",
  "region": "Updated Region",
  "created_at": "2025-05-01T14:30:00",
  "updated_at": "2025-05-01T14:31:00",
  "is_deleted": false
}
```

#### 8. Delete School (Soft Delete)
```http
DELETE /api/v1/schools/{school_id}
Authorization: Bearer {admin_token}

Response:
{
  "message": "School deleted successfully"
}
```

## Validation Rules

### Email
- Must be valid email format (RFC 5322)
- Must be unique across all users
- Case-insensitive (stored as lowercase)

### Password (Required for all users)
- Minimum 12 characters
- Must contain at least one uppercase letter (A-Z)
- Must contain at least one lowercase letter (a-z)
- Must contain at least one digit (0-9)
- Must contain at least one special character (!@#$%^&*(),.?":{}|<>)

### Role (During Registration)
- Public endpoint: Only `teacher` or `student` allowed
- Cannot create `admin` via public registration
- Admin accounts must be created by other admins

### School ID
- Must be a valid UUID
- School must exist and not be deleted
- Required for teacher/student registration
- Optional (NULL) for admin accounts

## Security Features

1. **Password Hashing**: Uses bcrypt with 12 salt rounds
2. **Token Authentication**: JWT-based with:
   - Access tokens (short-lived)
   - Refresh tokens (long-lived, rotated on use)
3. **Role-Based Access Control**: 
   - Public endpoints for registration
   - Admin-only endpoints for management
   - Teachers/students can only access their own school's resources
4. **Soft Deletes**: Users and schools marked as deleted but not removed
5. **Email Normalization**: All emails converted to lowercase

## Important Notes

### Bootstrap Admin
- Auto-created on first application startup
- Email: `admin@visiolearn.org`
- Password: `AdminPass123!@` (set in `app/main.py`)
- Bootstrap endpoint (`POST /api/v1/users/bootstrap`) only works if no users exist

### School Selection
- Visible to public during registration
- Teachers/students are permanently assigned to a school on registration
- To change school: Admin can create new account with different school_id
- Cannot self-update school_id

### Teachers vs Students
- Both created via same registration endpoint
- Role determines permissions and capabilities
- School_id scopes both to their assigned school

### Admin Accounts
- Cannot be created via public registration
- Only admins can create other admins
- Admins are system-wide (not scoped to schools)
- At least one admin should always exist

## Migration from Old System

If upgrading from admin-only user creation:

1. **Create Schools First**
   - Admin logs in
   - Creates all schools via POST `/api/v1/schools`
   - Saves school IDs

2. **Manually Migrate Existing Users** (if any)
   - Export existing users from old system
   - Use POST `/api/v1/users` (admin endpoint) to recreate them
   - Or delete and have users self-register

3. **Communicate New Flow to Users**
   - Share school creation is complete
   - Distribute registration link with school info
   - Users can now self-register

## Troubleshooting

### "Email already registered"
- Check if email was used in a previous registration
- Use a different email address
- Contact admin to check email uniqueness

### "School not found or has been deactivated"
- Verify school_id is correct
- Check that school hasn't been deleted
- Use GET `/api/v1/schools/public` to see available schools

### "Incorrect email or password"
- Ensure email matches exactly (case-insensitive)
- Verify password is correct
- Check caps lock
- Confirm account creation was successful

### "Invalid password"
- Must be at least 12 characters
- Must include uppercase, lowercase, digit, and special character
- Example valid: `TeacherPass123!@`

### "Invalid role"
- Public registration only allows `teacher` or `student`
- Contact admin to create admin accounts
- Use POST `/api/v1/users` (admin endpoint) for that

## Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `email` (String, Unique, NOT NULL)
- `full_name` (String, NOT NULL)
- `role` (String: admin|teacher|student, NOT NULL)
- `school_id` (UUID, Foreign Key → Schools.id, NULL for admins)
- `hashed_password` (String, NOT NULL)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_deleted` (Boolean, default False)
- `last_login_at` (DateTime, nullable)

### Schools Table
- `id` (UUID, Primary Key)
- `name` (String, NOT NULL)
- `region` (String, nullable)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `is_deleted` (Boolean, default False)

## Implementation Files Changed

1. **app/schemas.py**
   - Added `UserRegister` schema (public registration)
   - Added `SchoolPublicResponse` schema (public school list)

2. **app/routers/auth.py**
   - Added `POST /api/v1/auth/register` endpoint
   - Validates school_id and email uniqueness
   - Restricts role to teacher|student only

3. **app/routers/schools.py**
   - Added `GET /api/v1/schools/public` endpoint
   - Returns school list for registration flow

4. **app/main.py**
   - Removed emoji characters (Windows compatibility)
   - Bootstrap admin creation on startup (unchanged)

## Future Enhancements

- [ ] Email verification before activation
- [ ] Invite-only registration (codes)
- [ ] Social login (Google, Microsoft)
- [ ] SAML/LDAP integration for schools
- [ ] Registration approval workflow
- [ ] Bulk user import from CSV
- [ ] User role change after registration (admin-only)
