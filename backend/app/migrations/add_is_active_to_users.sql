-- Migration: add is_active column to users table
-- Run once against your PostgreSQL database.
-- Existing users are set to active=true so they are not locked out.

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Existing users without MFA are already active — no change needed.
-- New users created via /auth/register will have is_active=false until
-- they complete MFA verification via /auth/register/verify.
