-- Disable email confirmation for development
-- Run this in your Supabase SQL Editor

UPDATE auth.config 
SET enable_signup = true, 
    enable_confirmations = false 
WHERE id = 'default';

-- Optional: Also disable phone confirmations if you're using phone auth
UPDATE auth.config 
SET enable_phone_confirmations = false 
WHERE id = 'default'; 