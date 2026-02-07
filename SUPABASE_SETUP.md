# Supabase Configuration Guide

This guide explains how to get your Supabase credentials for file storage.

## Step-by-Step Instructions

### 1. Create/Login to Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Sign in or create a free account
3. Create a new project or select an existing project

### 2. Get Your Project URL (SUPABASE_URL)

1. In your Supabase project dashboard, click on the **Settings** icon (gear icon) in the left sidebar
2. Click on **API** in the settings menu
3. Under **Project URL**, you'll see your project URL
   - Format: `https://xxxxxxxxxxxxx.supabase.co`
   - Copy this value → This is your `SUPABASE_URL`

### 3. Get Your API Key (SUPABASE_KEY)

1. Still in the **API** settings page
2. You'll see two keys:
   - **anon public** key - Use this for client-side operations (recommended for most cases)
   - **service_role** key - Use this for server-side admin operations (more powerful, keep secret!)
3. Copy the **anon public** key → This is your `SUPABASE_KEY`
   - ⚠️ **Note**: For file uploads from the backend, you might need the `service_role` key instead

### 4. Create Storage Bucket (SUPABASE_STORAGE_BUCKET)

1. In your Supabase dashboard, click on **Storage** in the left sidebar
2. Click **New bucket** button
3. Enter a bucket name (e.g., `jobboard-files`, `resumes`, `profile-pictures`)
4. Choose bucket settings:
   - **Public bucket**: Check if files should be publicly accessible
   - **File size limit**: Set maximum file size (e.g., 5MB for resumes)
   - **Allowed MIME types**: Restrict file types if needed
5. Click **Create bucket**
6. The bucket name you created → This is your `SUPABASE_STORAGE_BUCKET`

### 5. Configure Bucket Policies (Important!)

After creating the bucket, you need to set up policies for access:

1. Click on your bucket name
2. Go to **Policies** tab
3. Click **New Policy**
4. For **public buckets** (profile pictures, public files):
   - Policy name: `Public Access`
   - Allowed operation: `SELECT` (read)
   - Target roles: `anon`, `authenticated`
   - Policy definition: `true` (allow all)

5. For **private buckets** (resumes, private files):
   - Policy name: `Authenticated Upload`
   - Allowed operation: `INSERT`, `UPDATE`, `DELETE`
   - Target roles: `authenticated`
   - Policy definition: `true` (or add custom conditions)

### 6. Update Your .env File

Add these values to your `.env` file:

```env
# Supabase Storage Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key-here
SUPABASE_STORAGE_BUCKET=your-bucket-name
```

### Example Configuration

```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzODk2NzIwMCwiZXhwIjoxOTU0NTQzMjAwfQ.example
SUPABASE_STORAGE_BUCKET=jobboard-files
```

## Quick Reference

| Variable | Where to Find | Example |
|----------|---------------|---------|
| `SUPABASE_URL` | Settings > API > Project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Settings > API > anon public key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_STORAGE_BUCKET` | Storage > Bucket name | `jobboard-files` |

## Security Notes

1. **Never commit your `.env` file** to version control
2. Use **anon key** for client-side operations
3. Use **service_role key** only on the backend server (never expose to frontend)
4. Set appropriate bucket policies to control access
5. For production, use environment variables or secret management services

## Troubleshooting

### "Invalid API key" error
- Make sure you copied the entire key (they're very long)
- Check if you're using the correct key type (anon vs service_role)

### "Bucket not found" error
- Verify the bucket name is spelled correctly
- Make sure the bucket exists in your Supabase project
- Check that you're using the correct project

### "Permission denied" error
- Check your bucket policies
- Verify you're using the correct API key (service_role for admin operations)
- Ensure the bucket is set to public if you need public access

## Additional Resources

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Supabase Storage Policies](https://supabase.com/docs/guides/storage/security/access-control)
- [Supabase API Reference](https://supabase.com/docs/reference)
