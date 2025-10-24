# bardclean - Core Functionality & File Type Safety
<!-- File: /home/mlj/utono/bardclean/TASKS-01.md -->

## Milestone 1: Core Functionality & File Type Safety (8-12 hours)

This milestone focuses on critical safety features that prevent destructive
processing of poetry files and improve the accuracy of dialogue detection in
plays. These features are foundational for all subsequent work.

**Priority:** P0 (Critical - Must complete before agent integration)

**Dependencies:** None (can start immediately)

**Deliverables:**
- File type detection system
- Enhanced dialogue processing
- Poetry protection mechanism

---

## Phase 1.1: File Type Detection System (FR-1 from PRD.md)

### Overview
Implement automatic file type detection to distinguish between plays, narrative
poems, sonnets, and lyric poems based on structural features.

**Estimated time:** 3-4 hours

### Tasks

- [1.1.1] [X] Create FileTypeFeatures dataclass
  a. Add character_names: List[str] field
  b. Add stage_direction_count: int field
  c. Add act_scene_count: int field
  d. Add quoted_dialogue_count: int field
  e. Add roman_numeral_markers: List[str] field
  f. Add has_narrator_tags: bool field
  g. Import dataclass from dataclasses module

- [1.1.2] [X] Implement feature extraction method
  a. Create extract_features(content: str) method in DialogueProcessor
  b. Scan for character names using CHAR_NAME_PATTERN
  c. Count stage directions using STAGE_DIR_PATTERN
  d. Detect ACT/SCENE markers with regex r'^(ACT|SCENE)'
  e. Find quoted dialogue with pattern r"^\s*'[A-Z]"
  f. Search for narrator tags: quoth, thus she, thus he
  g. Detect Roman numerals: I, II, III, IV, V, VI, VII, VIII, IX, X
  h. Return FileTypeFeatures instance

- [1.1.3] [X] Implement file type classification logic
  a. Create detect_file_type(features: FileTypeFeatures) method
  b. Play detection: has character_names AND stage_directions
  c. Sonnet detection: has roman_numerals AND NOT character_names
  d. Narrative detection: has quoted_dialogue AND narrator_tags
  e. Lyric detection: NOT character_names AND NOT stage_directions
  f. Return tuple: (file_type: str, confidence: float)

- [1.1.4] [X] Implement confidence scoring algorithm
  a. Calculate confidence based on feature strength
  b. Play confidence: 0.9 if both features, 0.7 if one
  c. Sonnet confidence: 0.95 if roman numerals > 10
  d. Narrative confidence: 0.8 if both quoted dialogue and narrator tags
  e. Lyric confidence: 0.6 (low certainty for pure poetry)
  f. Return confidence score 0.0-1.0

- [1.1.5] [X] Add file type detection to main processing flow
  a. Call extract_features() at start of process_file()
  b. Call detect_file_type() with extracted features
  c. Store file_type and confidence in instance variables
  d. Log detection result if verbose mode enabled
  e. Use file type to determine processing mode

### Verification Checklist
- [X] FileTypeFeatures dataclass has all required fields
- [X] Feature extraction finds all character names in test files
- [X] Correctly identifies all 38 plays as type "play"
- [X] Correctly identifies sonnets_gut.txt as type "sonnet"
- [X] Correctly identifies venus_and_adonis_gut.txt as "narrative_poem"
- [X] Confidence scores are reasonable (≥0.8 for plays)
- [X] Low confidence triggers warning message

---

## Phase 1.2: Enhanced Dialogue Processing

### Overview
Improve the existing dialogue detection state machine to handle edge cases
and track processing statistics for better reporting.

**Estimated time:** 2-3 hours

### Tasks

- [1.2.1] [X] Enhance character name detection accuracy
  a. Verify CHAR_NAME_PATTERN handles mixed case (e.g., "Ber.")
  b. Verify CHAR_NAME_PATTERN handles ALL CAPS (e.g., "HAMLET.")
  c. Verify CHAR_NAME_PATTERN handles multi-word (e.g., "First Musician.")
  d. Add length validation: reject if > 30 characters
  e. Add ACT/SCENE exclusion: reject if starts with ACT or SCENE
  f. Add test cases for each pattern variation

- [1.2.2] [X] Document and validate state machine transitions
  a. Add docstring explaining state machine to DialogueProcessor
  b. Document Initial state (not in dialogue)
  c. Document Dialogue state (processing dialogue lines)
  d. Document transition: character_name → enter dialogue
  e. Document transition: blank_line → exit dialogue
  f. Document transition: stage_direction → exit dialogue
  g. Add assertions to validate state consistency

- [1.2.3] [X] Add dialogue line tracking
  a. Add self.dialogue_lines_processed counter
  b. Increment when processing line in dialogue mode
  c. Add self.non_dialogue_lines_skipped counter
  d. Increment when skipping non-dialogue lines
  e. Include counts in processing result
  f. Add reset() method to clear counters between files

- [1.2.4] [X] Improve blank line handling
  a. Ensure blank lines always exit dialogue mode
  b. Handle lines with only whitespace
  c. Don't count blank lines in dialogue_lines_processed
  d. Test with files that have inconsistent blank line usage

- [1.2.5] [X] Add edge case handling
  a. Handle character names without following dialogue
  b. Handle stage directions in middle of dialogue block
  c. Handle very short dialogue lines (< 3 characters)
  d. Handle dialogue lines that are only punctuation
  e. Test with edge cases from planning.md

### Verification Checklist
- [ ] Character name pattern matches all formats from planning.md
- [ ] State machine handles all transition scenarios
- [ ] Dialogue line counter matches expected values
- [ ] Blank lines correctly exit dialogue mode
- [ ] Edge cases don't cause crashes or incorrect processing

---

## Phase 1.3: Poetry Protection System (FR-4 from PRD.md)

### Overview
Implement safety features to block processing of pure poetry files by default,
requiring explicit --force flag override with clear warnings.

**Estimated time:** 2-3 hours

### Tasks

- [1.3.1] [X] Implement poetry detection and blocking
  a. Add check_if_poetry() method
  b. Return True if file_type in ['sonnet', 'lyric_poem']
  c. Call check after file type detection
  d. Raise PoetryFileError if poetry detected and not forced
  e. Create custom PoetryFileError exception class

- [1.3.2] [X] Create clear error messages for blocked files
  a. Error format: "Error: File detected as '{file_type}' (pure poetry)."
  b. Add explanation: "This file contains Shakespeare's authorial poetry..."
  c. Add instruction: "Use --force to override (not recommended)."
  d. Include confidence score in error message
  e. Provide example of what would be damaged

- [1.3.3] [X] Add --force flag support
  a. Add --force argument to ArgumentParser
  b. Pass force flag to DialogueProcessor
  c. Skip poetry check if force=True
  d. Log warning even with --force: "WARNING: Force-processing poetry file"
  e. Include force status in processing result

- [1.3.4] [X] Add narrative poem warning (not blocking)
  a. Detect narrative_poem file type
  b. Show warning: "Warning: Narrative poem detected"
  c. Explain: "This contains quoted dialogue in verse context"
  d. Don't block, but require user confirmation if interactive
  e. Log narrative poem processing attempts

- [1.3.5] [X] Test poetry protection with all poetry files
  a. Test sonnets_gut.txt blocks without --force
  b. Test sonnets_gut.txt processes with --force
  c. Test lyric poems block correctly
  d. Test narrative poems show warning but don't block
  e. Verify error messages are clear and actionable

### Verification Checklist
- [X] All sonnet files blocked by default
- [X] All lyric poem files blocked by default
- [X] Error message explains why processing would be destructive
- [X] --force flag successfully overrides block
- [X] Warning logged even when --force used
- [X] Narrative poems trigger warning but don't block
- [X] Processing result includes force_used flag

---

## Phase 1.4: Backup and Permission Enhancement

### Overview
Ensure backup system is robust and permission handling works correctly in all
scenarios, including edge cases like already-existing backups.

**Estimated time:** 1-2 hours

### Tasks

- [1.4.1] [X] Enhance backup creation logic
  a. Check if .bak file already exists
  b. Rename existing .bak to .bak.1 (keep one previous backup)
  c. Create new .bak from current file
  d. Copy permissions from original to backup
  e. Verify backup creation before processing
  f. Abort if backup creation fails

- [1.4.2] [X] Improve permission restoration
  a. Store original_mode before any changes
  b. Use try/finally to ensure restoration
  c. Restore permissions even if processing fails
  d. Apply same permissions to backup file
  e. Log permission changes if verbose mode
  f. Test with read-only files

- [1.4.3] [X] Add permission error handling
  a. Catch PermissionError during chmod operations
  b. Provide clear error message with file path
  c. Suggest running with appropriate permissions
  d. Don't leave file in inconsistent state
  e. Clean up partial changes on permission error

### Verification Checklist
- [ ] Backup created successfully before modification
- [ ] Existing backups renamed, not overwritten
- [ ] Permissions restored on success
- [ ] Permissions restored on failure
- [ ] Backup has same permissions as original
- [ ] Clear error messages for permission issues

---

## Phase 1.5: Structure Metadata Generation for Agents

### Overview
Generate companion .structure.json files for each Shakespeare text that provide
structural metadata and processing guidance for coding agents. These files
enable agents to understand file contents without re-analyzing.

**Estimated time:** 2-3 hours

### Tasks

- [1.5.1] [ ] Create FileStructureMetadata dataclass
  a. Add filepath: str field
  b. Add file_type: str field (play, sonnet, narrative_poem, lyric_poem)
  c. Add confidence: float field
  d. Add is_processable: bool field
  e. Add processing_recommendation: str field
  f. Add features: FileTypeFeatures field
  g. Add metadata: Dict[str, Any] for additional info
  h. Add analyzed_date: str field (ISO timestamp)

- [1.5.2] [ ] Implement metadata generation
  a. Create generate_structure_metadata() method
  b. Use extract_features() from Phase 1.1
  c. Use detect_file_type() from Phase 1.1
  d. Extract title from file header
  e. Count total lines in file
  f. Estimate dialogue percentage for plays
  g. Return FileStructureMetadata instance

- [1.5.3] [ ] Add play-specific metadata extraction
  a. Extract all character names (unique list)
  b. Count total acts and scenes
  c. Extract scene locations if available
  d. Count stage directions
  e. Estimate dialogue lines vs total lines ratio
  f. Store in metadata dict under 'play_structure'

- [1.5.4] [ ] Add sonnet-specific metadata extraction
  a. Count number of sonnets (Roman numeral sections)
  b. Extract sonnet numbers (I, II, III, etc.)
  c. Verify 14-line structure
  d. Note rhyme scheme if detectable
  e. Store in metadata dict under 'sonnet_structure'

- [1.5.5] [ ] Add narrative poem metadata extraction
  a. Count quoted dialogue sections
  b. Identify narrator voice vs character voice ratio
  c. Extract character names from quoted dialogue
  d. Count stanzas
  e. Store in metadata dict under 'narrative_structure'

- [1.5.6] [ ] Implement JSON serialization
  a. Create to_json() method on FileStructureMetadata
  b. Use json.dumps() with indent=2 for readability
  c. Handle datetime serialization (ISO format)
  d. Include schema version number
  e. Return formatted JSON string

- [1.5.7] [ ] Add companion file writing
  a. Create write_structure_file() method
  b. Generate filename: original + '.structure.json'
  c. Write JSON to companion file
  d. Use same directory as original file
  e. Handle write errors gracefully
  f. Log companion file creation

- [1.5.8] [ ] Add --generate-metadata flag
  a. Add argument to ArgumentParser
  b. Flag enables metadata generation
  c. Can be combined with --validate
  d. Can be run on entire directory
  e. Update help text with examples

- [1.5.9] [ ] Create batch metadata generation utility
  a. Add generate_all_metadata() function
  b. Find all .txt files in directory
  c. Generate metadata for each file
  d. Skip if .structure.json already exists (unless --force)
  e. Report summary: X files analyzed, Y metadata files created

### Verification Checklist
- [ ] Metadata files created with .structure.json extension
- [ ] JSON format is valid and readable
- [ ] Play metadata includes character names and act/scene info
- [ ] Sonnet metadata includes sonnet count
- [ ] Narrative poem metadata includes dialogue sections
- [ ] Metadata accurately reflects file content
- [ ] Agents can parse JSON without errors
- [ ] Companion files placed in same directory as originals

### Example Output Format

```json
{
  "schema_version": "1.0",
  "filepath": "/path/to/hamlet_gut.txt",
  "analyzed_date": "2025-10-20T14:30:00Z",
  "file_type": "play",
  "confidence": 0.99,
  "is_processable": true,
  "processing_recommendation": "Safe to process as play - dialogue mode",
  "features": {
    "character_names": ["HAMLET", "OPHELIA", "CLAUDIUS", "GERTRUDE"],
    "character_count": 34,
    "stage_direction_count": 245,
    "act_scene_count": 20,
    "quoted_dialogue_count": 0,
    "roman_numeral_markers": [],
    "has_narrator_tags": false
  },
  "metadata": {
    "title": "HAMLET, PRINCE OF DENMARK",
    "author": "William Shakespeare",
    "total_lines": 6301,
    "estimated_dialogue_lines": 2076,
    "dialogue_percentage": 33,
    "play_structure": {
      "acts": 5,
      "scenes": 20,
      "major_characters": [
        "HAMLET", "CLAUDIUS", "GERTRUDE", "OPHELIA", "POLONIUS"
      ],
      "locations": [
        "Elsinore. A platform before the Castle",
        "A room of state in the Castle"
      ]
    }
  }
}
```

---

## Milestone 1: Overall Verification

### Functional Requirements Coverage
- [x] FR-1: File Type Detection implemented
- [x] FR-4: Poetry Protection implemented
- [x] FR-5: File Permission Handling enhanced
- [x] FR-6: Backup Creation improved

### Testing Requirements for Milestone 1
- [ ] Test with all 38 Shakespeare plays (automated)
- [ ] Test with sonnets_gut.txt (should block)
- [ ] Test with narrative poems (should warn)
- [ ] Test with lyric poems (should block)
- [ ] Test character name detection with mixed formats
- [ ] Test state machine with edge cases
- [ ] Test permission handling with read-only files
- [ ] Test backup creation and restoration

### Success Metrics
- [ ] File type detection accuracy ≥ 95% on known corpus
- [ ] Zero false positives (plays detected as poetry)
- [ ] Zero false negatives (poetry detected as plays)
- [ ] All 38 plays process successfully
- [ ] All 4+ poetry files blocked by default
- [ ] Poetry files process only with --force
- [ ] Backups created for 100% of processed files
- [ ] Permissions restored in 100% of cases

### Documentation Requirements
- [ ] Add docstrings to all new methods
- [ ] Document file type detection algorithm
- [ ] Document state machine transitions
- [ ] Update README.md with --force flag
- [ ] Add comments explaining poetry protection logic

---

## Next Steps

After completing Milestone 1, proceed to TASKS-02.md (Command-Line Interface &
Validation) which builds on the file type detection system to provide
validation mode and enhanced CLI features.
