-- Run once against the existing Railway/Postgres database.
ALTER TABLE projects ADD COLUMN IF NOT EXISTS architecture JSON;
