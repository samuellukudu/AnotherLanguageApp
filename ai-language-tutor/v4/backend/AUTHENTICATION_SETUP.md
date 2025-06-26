# Authentication Setup Guide

This guide will help you set up authentication for your FastAPI backend with Supabase.

## 1. Supabase Project Setup

### Create Supabase Project
1. Go to [Supabase](https://supabase.com) and create a new project
2. Wait for the project to be fully provisioned

### Get Configuration Values
1. Go to your project settings > API
2. Copy the following values:
   - **Project URL** (SUPABASE_URL)
   - **Anon/Public Key** (SUPABASE_KEY)

### Get JWT Secret
1. Go to your project settings > API
2. Copy the **JWT Secret** (SUPABASE_JWT_SECRET)

## 2. Environment Configuration

Create a `.env` file in your backend directory with:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_public_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Optional: Database Configuration
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# FastAPI Configuration
DEBUG=True
ENVIRONMENT=development
```

## 3. Database Setup

### Create Users Table
Run the SQL from `database_setup.sql` in your Supabase SQL editor:

1. Go to your Supabase project
2. Navigate to the SQL Editor
3. Copy and paste the contents of `backend/database_setup.sql`
4. Execute the script

### Configure Authentication
1. Go to Authentication > Settings
2. Configure the following:
   - **Site URL**: Your frontend URL (e.g., `http://localhost:3000`)
   - **Email confirmation**: Enable if you want email verification
   - **Password strength**: Configure as needed

## 4. Testing Authentication

### Test Registration
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "username": "testuser"
  }'
```

### Test Login
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### Test Protected Endpoint
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 5. Common Issues & Solutions

### Issue: "JWT secret not configured"
- **Solution**: Make sure `SUPABASE_JWT_SECRET` is set in your environment

### Issue: "Token validation failed"
- **Solution**: Check that you're using the correct JWT secret from Supabase settings

### Issue: "User registration failed"
- **Solutions**:
  - Check if email confirmation is required in Supabase auth settings
  - Ensure the users table exists and has correct permissions
  - Check Supabase logs for detailed error messages

### Issue: "Invalid email or password"
- **Solutions**:
  - Verify the user has confirmed their email (if required)
  - Check that the password meets your configured requirements
  - Ensure the user exists in Supabase auth

### Issue: Database connection errors
- **Solutions**:
  - Verify your Supabase URL and key are correct
  - Check your internet connection
  - Ensure your Supabase project is active

## 6. Security Best Practices

1. **Environment Variables**: Never commit `.env` files to version control
2. **JWT Secret**: Keep your JWT secret secure and rotate it periodically
3. **Password Policy**: Configure strong password requirements in Supabase
4. **Rate Limiting**: Consider implementing rate limiting for auth endpoints
5. **HTTPS**: Always use HTTPS in production
6. **Token Expiration**: Configure appropriate token expiration times

## 7. API Endpoints

After setup, you'll have these endpoints available:

- `POST /users/register` - Register new user
- `POST /users/login` - Authenticate user
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/profile/{user_id}` - Get specific user profile (admin)
- `PUT /users/profile/{user_id}` - Update specific user profile (admin)

## 8. Frontend Integration

When integrating with your frontend:

1. Store the access token securely (e.g., in httpOnly cookies or secure storage)
2. Include the token in the Authorization header: `Bearer <token>`
3. Handle token expiration and refresh as needed
4. Implement proper logout functionality

## Need Help?

If you encounter issues:
1. Check the application logs for detailed error messages
2. Review Supabase project logs in the dashboard
3. Ensure all environment variables are correctly set
4. Verify the database schema is properly created 