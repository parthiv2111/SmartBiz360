# Fix: Logout on Server Restart Issue

## Problem
Users are being logged out every time the server restarts because the `JWT_SECRET_KEY` is not persistent.

## Solution

### Option 1: Auto-Generate .env File (Recommended)

Run this command in the `backend` directory:

```bash
python create_env.py
```

This will automatically create a `.env` file with secure, persistent keys.

### Option 2: Manual Setup

1. Create a `.env` file in the `backend` directory:

```bash
cd backend
touch .env
```

2. Add the following content to `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smartbiz360

# Security Configuration - IMPORTANT: Use persistent keys!
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173

# File Upload Configuration
UPLOAD_FOLDER=uploads

# Environment
FLASK_ENV=development
FLASK_DEBUG=True
```

3. **IMPORTANT**: Replace the placeholder values with actual secure keys:

```bash
# Generate secure keys (run in Python)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32)); print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Option 3: Quick Fix (Development Only)

For quick testing, you can use fixed keys in `.env`:

```env
JWT_SECRET_KEY=dev-jwt-secret-key-do-not-use-in-production-12345
SECRET_KEY=dev-secret-key-do-not-use-in-production-12345
```

**⚠️ Warning**: Never use these keys in production!

## Verification

After setting up `.env`:

1. Restart your server
2. Log in
3. Restart the server again
4. You should **NOT** be logged out

## Why This Happens

- JWT tokens are signed with `JWT_SECRET_KEY`
- If the secret key changes, all existing tokens become invalid
- Without a `.env` file, the app uses a default key that might change
- With a persistent `.env` file, the same key is used every time

## Security Notes

- ✅ Keep `.env` file secure
- ✅ Never commit `.env` to version control (it's in `.gitignore`)
- ✅ Use different keys for development and production
- ✅ Use strong, randomly generated keys in production

