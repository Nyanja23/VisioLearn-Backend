# Using /internal/create-admin Endpoint

This endpoint is a **temporary workaround** for Render's free tier which doesn't provide shell access.

## Setup Instructions

### 1. Add ADMIN_SECRET to Render Environment Variables

1. Go to Render Dashboard → Your Service
2. Click **Environment** tab
3. Add a new environment variable:
   - **Key:** `ADMIN_SECRET`
   - **Value:** Use any strong random string (e.g., `your-super-secret-key-12345`)

### 2. Create the Admin Account

Make a POST request to:
```
https://visiolearn-backend.onrender.com/internal/create-admin
```

**Request Body:**
```json
{
  "email": "admin@visiolearn.org",
  "password": "AdminPass123!@",
  "secret": "your-super-secret-key-12345"
}
```

**Using curl:**
```bash
curl -X POST https://visiolearn-backend.onrender.com/internal/create-admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@visiolearn.org",
    "password": "AdminPass123!@",
    "secret": "your-super-secret-key-12345"
  }'
```

### 3. Expected Response (Success)

```json
{
  "status": "created",
  "message": "Admin user created successfully",
  "email": "admin@visiolearn.org",
  "role": "admin",
  "id": "xxx-xxx-xxx",
  "warning": "DELETE OR DISABLE THIS ENDPOINT AFTER FIRST USE"
}
```

### 4. Verify Admin Created

Check the health endpoint:
```
https://visiolearn-backend.onrender.com/health
```

Should show:
```json
{
  "status": "healthy",
  "database": "connected",
  "admin_exists": true,
  "admin_email": "admin@visiolearn.org"
}
```

### 5. Login Should Now Work

- **Email:** `admin@visiolearn.org`
- **Password:** `AdminPass123!@`

---

## IMPORTANT: Disable After Use

⚠️ **After creating the admin, you MUST disable this endpoint:**

### Option A: Delete the Endpoint (Recommended)
Remove the `/internal/create-admin` endpoint code from `app/routers/auth.py`

### Option B: Disable with Empty Secret
1. Go to Render Environment Variables
2. Set `ADMIN_SECRET` to empty string `""`
3. The endpoint will return 403 Forbidden

---

## Troubleshooting

### 403 Forbidden - Invalid secret
- Check that `ADMIN_SECRET` is set in Render environment variables
- Make sure the secret in your request matches exactly

### 400 Bad Request - Admin already exists
- The admin with that email already exists
- You can try a different email or check the database

### 500 Internal Server Error
- Check Render logs for more details
- Make sure DATABASE_URL environment variable is set correctly

---

## Why This Exists

On Render's free plan:
- ❌ No shell access to run `python bootstrap_admin.py`
- ❌ Can't run migrations manually
- ✅ Can make HTTP requests

This endpoint provides a temporary workaround. It will be removed in future versions when:
- Using a paid Render plan with shell access
- Or switching to a different hosting provider
- Or using a deployment script that handles admin creation automatically
