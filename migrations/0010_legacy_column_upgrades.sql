-- Conditional legacy-column upgrades are versioned and checksum-protected.
-- The directive skips only the ALTER when that column already exists.
-- @add-column-if-missing legal_documents practice_area
ALTER TABLE legal_documents ADD COLUMN practice_area TEXT NOT NULL DEFAULT 'unknown';

-- @add-column-if-missing users active
ALTER TABLE users ADD COLUMN active INT DEFAULT 1;

-- @add-column-if-missing chunks verified
ALTER TABLE chunks ADD COLUMN verified INT DEFAULT 0;

-- @add-column-if-missing chunks document_version_id
ALTER TABLE chunks ADD COLUMN document_version_id INT;

-- @add-column-if-missing chunks page
ALTER TABLE chunks ADD COLUMN page TEXT;

-- These columns are not prerequisites for immutable migrations 0001-0009.
-- @add-column-if-missing docs firm_id
ALTER TABLE docs ADD COLUMN firm_id INT;

-- @add-column-if-missing docs uploader_user_id
ALTER TABLE docs ADD COLUMN uploader_user_id INT;

-- @add-column-if-missing docs sha256
ALTER TABLE docs ADD COLUMN sha256 TEXT;

-- @add-column-if-missing docs content_type
ALTER TABLE docs ADD COLUMN content_type TEXT;

-- @add-column-if-missing docs byte_size
ALTER TABLE docs ADD COLUMN byte_size INT;

-- @add-column-if-missing docs extraction_status
ALTER TABLE docs ADD COLUMN extraction_status TEXT;

-- @add-column-if-missing docs ocr_used
ALTER TABLE docs ADD COLUMN ocr_used INT NOT NULL DEFAULT 0;

-- @add-column-if-missing document_extraction_reviews page_reference
ALTER TABLE document_extraction_reviews ADD COLUMN page_reference TEXT NOT NULL DEFAULT '';

-- @add-column-if-missing cases case_number
ALTER TABLE cases ADD COLUMN case_number TEXT DEFAULT '';

-- @add-column-if-missing cases case_year
ALTER TABLE cases ADD COLUMN case_year TEXT DEFAULT '';

-- @add-column-if-missing cases court
ALTER TABLE cases ADD COLUMN court TEXT DEFAULT '';

-- @add-column-if-missing cases circuit
ALTER TABLE cases ADD COLUMN circuit TEXT DEFAULT '';

-- @add-column-if-missing cases opposing_party
ALTER TABLE cases ADD COLUMN opposing_party TEXT DEFAULT '';

-- Preserve the legacy ownership backfill after docs.firm_id is guaranteed.
UPDATE docs
SET firm_id=(SELECT firm_id FROM cases WHERE cases.id=docs.case_id)
WHERE firm_id IS NULL;
