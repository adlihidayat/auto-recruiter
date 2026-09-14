ALTER TABLE transcripts DROP COLUMN reasoning;
ALTER TABLE transcripts DROP COLUMN trigger_matched;
ALTER TABLE transcripts ADD COLUMN progression_override BOOLEAN DEFAULT FALSE;
