# Product Requirements Document: Shakespeare Dialogue Punctuation Processor

**Version:** 1.0
**Date:** 2025-10-20
**Status:** Planning Phase
**Target Users:** Human users, Coding agents/AI assistants

---

## Executive Summary

A Python-based tool to intelligently strip specific punctuation marks from dialogue lines in Shakespeare texts while preserving sentence-ending and question punctuation. The tool distinguishes between different Shakespeare file types (plays, narrative poems, pure poetry) and only processes appropriate content to avoid damaging poetic works.

---

## Problem Statement

### Current Situation
Shakespeare texts from Project Gutenberg contain full punctuation that may interfere with certain text analysis workflows or reading experiences. Users need a way to selectively remove punctuation from **dialogue only** while:
- Preserving sentence structure (periods)
- Preserving questions (question marks)
- Maintaining word contractions (apostrophes)
- Avoiding damage to non-dialogue content (stage directions, metadata)
- **Critically**: Not processing pure poetry as if it were dialogue

### Why This Matters
1. **Dialogue vs Poetry Distinction**: Sonnets and lyric poems are authorial voice, not character dialogue
2. **Structural Preservation**: Stage directions and metadata must remain intact
3. **File Type Safety**: Processing sonnets as plays would be destructive
4. **Automation Risk**: Coding agents need clear guidance on which files to process

---

## Goals & Objectives

### Primary Goals
1. Remove specific punctuation from Shakespeare play dialogue lines
2. Preserve essential punctuation (periods, question marks, apostrophes)
3. Automatically detect file types and prevent inappropriate processing
4. Provide safe batch processing for multiple files

### Secondary Goals
1. Enable coding agent integration with structured output
2. Support validation and dry-run modes
3. Provide detailed processing statistics
4. Create comprehensive documentation for file structures

### Success Criteria
- ✅ Correctly identifies and processes 38 Shakespeare plays
- ✅ Blocks processing of 4+ pure poetry files by default
- ✅ Provides warnings for 2 narrative poem files
- ✅ Maintains read-only permissions on original files
- ✅ Creates backups before modification
- ✅ Provides JSON output for programmatic access

---

## User Stories

### Human Users

**Story 1: Process a Single Play**
```
As a Shakespeare scholar
I want to remove punctuation from Hamlet's dialogue
So that I can analyze speech patterns without punctuation noise

Acceptance Criteria:
- Script removes commas, semicolons, colons, exclamation marks, quotes, dashes
- Script preserves periods, question marks, apostrophes
- Original file remains read-only
- Backup is created
```

**Story 2: Batch Process Multiple Plays**
```
As a digital humanities researcher
I want to process all Shakespeare plays at once
So that I can create a consistent corpus

Acceptance Criteria:
- Can select multiple files via fzf or command line
- Each file processed independently
- Summary statistics provided
- Failures don't stop batch processing
```

**Story 3: Avoid Processing Poetry**
```
As a user with mixed Shakespeare files
I want the tool to refuse processing sonnets
So that I don't accidentally damage lyric poetry

Acceptance Criteria:
- Tool detects file type automatically
- Blocks processing of sonnets by default
- Provides clear error message
- Requires explicit --force flag to override
```

### Coding Agents

**Story 4: Validate Before Processing**
```
As a coding agent
I want to validate file structure before processing
So that I can ensure files are appropriate for processing

Acceptance Criteria:
- JSON output with file type classification
- Confidence scores for detection
- List of detected features
- Processing recommendations
```

**Story 5: Safe Batch Processing**
```
As a coding agent
I want to process only play files automatically
So that I don't damage poetry or narrative works

Acceptance Criteria:
- Auto-detect and filter by file type
- Process only "play" type files
- Log skipped files with reasons
- Provide structured output for all operations
```

---

## Functional Requirements

### FR-1: File Type Detection

**Priority:** P0 (Critical)

**Description:** Automatically detect Shakespeare file type based on content structure.

**File Types:**
1. **Play** - Character names, stage directions, dialogue
2. **Narrative Poem** - Narrative verse with quoted dialogue
3. **Sonnet** - 154 numbered lyric poems
4. **Lyric Poem** - Short pure poetry

**Detection Criteria:**

| Feature | Play | Narrative | Sonnet | Lyric |
|---------|------|-----------|--------|-------|
| Character names (e.g., `HAMLET.`) | ✓ | ✗ | ✗ | ✗ |
| Stage directions (`[Enter...]`) | ✓ | ✗ | ✗ | ✗ |
| ACT/SCENE markers | ✓ | ✗ | ✗ | ✗ |
| Quoted dialogue (`'...`) | ✗ | ✓ | ✗ | ✗ |
| Narrator tags (quoth, thus) | ✗ | ✓ | ✗ | ✗ |
| Roman numeral titles | ✗ | ✗ | ✓ | ✗ |

**Acceptance:**
- Detection accuracy ≥ 95% on known corpus
- Returns file type + confidence score
- Provides feature analysis

---

### FR-2: Dialogue Processing (Plays)

**Priority:** P0 (Critical)

**Description:** Strip punctuation from play dialogue lines using state machine.

**State Machine:**
- **Initial State**: Not in dialogue
- **Transition**: Character name detected → Enter dialogue mode
- **Exit**: Blank line, stage direction, or new character → Exit dialogue mode

**Processing Rules:**

| Content Type | Action |
|-------------|--------|
| Character name (e.g., `HAMLET.`) | Skip, enter dialogue mode |
| Stage direction (`[Exit]`) | Skip, exit dialogue mode |
| Blank line | Skip, exit dialogue mode |
| ACT/SCENE markers | Skip, stay in initial state |
| Metadata (cast list, etc.) | Skip, stay in initial state |
| Dialogue line (in dialogue mode) | Process: remove punctuation |
| Any line (not in dialogue mode) | Skip |

**Punctuation Removal:**
- **Remove**: `,` `;` `:` `!` `"` `-` `—` `–`
- **Preserve**: `.` `?` `'`

**Example:**
```
Input:  Call here my varlet; I'll unarm again.
Output: Call here my varlet I'll unarm again.

Input:  Who's there?
Output: Who's there?
```

---

### FR-3: Narrative Poem Processing (Optional)

**Priority:** P2 (Nice to Have)

**Description:** Process only quoted dialogue in narrative poems.

**Pattern:** Lines beginning with single quote `'`

**Processing Mode:**
- Process lines matching: `^\s*'[A-Z]`
- Skip narrator voice lines
- Preserve stanza structure

**Warning:** User must acknowledge potential impact on poetic meter.

---

### FR-4: Poetry Protection

**Priority:** P0 (Critical)

**Description:** Block processing of pure poetry files by default.

**Behavior:**
- Detect sonnets and lyric poems
- Return error message
- Suggest `--force` flag if user insists
- Log warning even with `--force`

**Error Message:**
```
Error: File detected as 'sonnet' (pure poetry).
This file contains Shakespeare's authorial poetry, not character dialogue.
Processing would strip punctuation from the author's work.
Use --force to override (not recommended).
```

---

### FR-5: File Permission Handling

**Priority:** P1 (Important)

**Description:** Handle read-only files gracefully.

**Behavior:**
1. Detect if file is read-only
2. Temporarily make writable
3. Process file
4. Restore original permissions
5. Apply same permissions to backup

**Edge Cases:**
- Permission denied → Clear error message
- Restore permissions even on processing failure

---

### FR-6: Backup Creation

**Priority:** P0 (Critical)

**Description:** Create `.bak` backup before processing.

**Behavior:**
- Backup created before any modification
- Backup inherits original file permissions
- Option to disable backup (agents only): `--no-backup`
- Backup overwrites existing `.bak` file

**Validation:**
- Backup must be created successfully before processing
- If backup fails, abort processing

---

### FR-7: Command-Line Interface

**Priority:** P0 (Critical)

**Arguments:**

```bash
# Positional
files...              # One or more .txt files to process

# Optional Flags
--dry-run            # Preview changes without modifying
--validate           # Check file structure and type
--json               # Output results as JSON
--file-type TYPE     # Force file type: play|narrative|poetry|auto
--force              # Override safety blocks
--no-backup          # Skip backup creation (for agents)
--stats-only         # Analyze without processing
--output-dir DIR     # Write to different directory
--verbose, -v        # Detailed output
--quiet, -q          # Minimal output
--help, -h           # Show help
--version            # Show version
```

**Examples:**

```bash
# Interactive file selection with fzf
python strip_dialogue_punctuation.py

# Process specific files
python strip_dialogue_punctuation.py hamlet_gut.txt macbeth_gut.txt

# Validate all files
python strip_dialogue_punctuation.py --validate --json *.txt

# Dry run on single file
python strip_dialogue_punctuation.py --dry-run hamlet_gut.txt

# Agent-friendly batch processing
python strip_dialogue_punctuation.py --json --no-backup *.txt

# Force processing poetry (not recommended)
python strip_dialogue_punctuation.py --force --file-type poetry sonnets_gut.txt
```

---

### FR-8: JSON Output Format

**Priority:** P1 (Important)

**Schema:**

```json
{
  "status": "success|error",
  "exit_code": 0,
  "timestamp": "2025-10-20T12:34:56Z",
  "files_processed": 1,
  "files_failed": 0,
  "results": [
    {
      "filepath": "/path/to/hamlet.txt",
      "status": "success",
      "file_type": {
        "detected": "play",
        "confidence": 0.99,
        "features": {
          "character_names": 34,
          "stage_directions": 245,
          "act_scene_markers": 5,
          "quoted_dialogue": 0
        }
      },
      "processing": {
        "mode": "dialogue",
        "total_lines": 6301,
        "dialogue_lines": 2076,
        "modified_lines": 2076,
        "unchanged_lines": 4225
      },
      "changes": {
        "punctuation_removed": {
          "commas": 1234,
          "semicolons": 456,
          "colons": 234,
          "exclamation_marks": 89,
          "quotation_marks": 12,
          "dashes": 67
        }
      },
      "backup_created": "/path/to/hamlet.txt.bak",
      "permissions_restored": true,
      "warnings": []
    }
  ]
}
```

---

### FR-9: Validation Mode

**Priority:** P1 (Important)

**Output:**

```json
{
  "file": "hamlet_gut.txt",
  "validation": {
    "is_shakespeare_file": true,
    "detected_type": "play",
    "confidence": 0.99,
    "is_processable": true,
    "processing_mode": "dialogue",
    "features": {
      "character_names": ["HAMLET", "OPHELIA", "CLAUDIUS"],
      "character_count": 34,
      "stage_direction_count": 245,
      "act_scene_count": 5,
      "quoted_dialogue_count": 0,
      "total_lines": 6301,
      "estimated_dialogue_lines": 2076
    },
    "warnings": [],
    "recommendation": "Safe to process as play"
  }
}
```

---

### FR-10: Exit Codes

**Priority:** P1 (Important)

**Codes:**

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | All files processed successfully |
| 1 | General error | Unspecified error occurred |
| 2 | File not found | Input file doesn't exist |
| 3 | Permission error | Cannot read/write file |
| 4 | Invalid file format | File is not processable Shakespeare text |
| 5 | Validation failed | File failed validation checks |
| 6 | No files to process | Empty file list |
| 7 | User cancelled | Interactive selection cancelled |

**Agent Usage:**
```python
result = subprocess.run(['python', 'strip_dialogue_punctuation.py', ...])
if result.returncode == 0:
    # Success
elif result.returncode == 4:
    # File type not processable
elif result.returncode == 5:
    # Validation failed
```

---

## Non-Functional Requirements

### NFR-1: Performance
- **Requirement:** Process 1MB file in < 5 seconds
- **Measurement:** Average of 3 runs on standard hardware

### NFR-2: Reliability
- **Requirement:** 99.9% success rate on known corpus
- **Measurement:** Test suite with 44 Shakespeare files

### NFR-3: Usability
- **Requirement:** Clear error messages for all failure modes
- **Measurement:** User testing with 5 participants

### NFR-4: Maintainability
- **Requirement:** Code coverage ≥ 80%
- **Measurement:** pytest with coverage plugin

### NFR-5: Compatibility
- **Requirement:** Python 3.8+
- **Dependencies:** Standard library only (subprocess, re, pathlib, stat)

### NFR-6: Documentation
- **Requirement:** Complete documentation for all file types
- **Deliverables:**
  - `shakespeare_file_structure.md`
  - `agent_usage.md`
  - `PRD.md` (this document)
  - `planning.md`

---

## Technical Specifications

### File Structure Support

**Supported Files:**
- ✅ 38 Shakespeare plays
- ⚠️ 2 narrative poems (with warnings)
- ❌ 4+ pure poetry collections (blocked by default)

**File Formats:**
- Input: UTF-8 text files
- Output: UTF-8 text files (same encoding)
- Backup: `.txt.bak` suffix

### Character Name Patterns

**Regular Expression:**
```python
CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]*\.$')
```

**Matches:**
- `HAMLET.`
- `OPHELIA.`
- `First Musician.`
- `LADY MACBETH.`

**Exclusions:**
- `ACT I.` (starts with ACT)
- `SCENE II.` (starts with SCENE)
- Lines > 30 characters (likely not character names)

### Stage Direction Patterns

**Regular Expression:**
```python
STAGE_DIR_PATTERN = re.compile(r'^\[.*\]$')
```

**Matches:**
- `[Enter HAMLET]`
- `[Exit Ghost]`
- `[Aside]`
- `[Thunder and lightning]`

### Punctuation Patterns

**Removal Pattern:**
```python
PUNCT_PATTERN = re.compile(r"[,;:!\"\-—–]")
```

**Preserves:**
- `.` (period) - sentence endings
- `?` (question mark) - questions
- `'` (apostrophe) - contractions

---

## Constraints & Assumptions

### Constraints
1. Input files must be Project Gutenberg Shakespeare texts
2. Files must use consistent formatting (character names, stage directions)
3. Python 3.8+ required
4. Read/write filesystem access required

### Assumptions
1. Users want to preserve sentence structure (periods)
2. Questions should remain marked (question marks)
3. Contractions are important (`'tis`, `don't`)
4. Pure poetry should not be processed
5. Backups are important for safety

---

## Out of Scope

### Version 1.0
- ❌ Processing non-Shakespeare texts
- ❌ Supporting other file formats (PDF, EPUB, etc.)
- ❌ Reversing changes (use backups instead)
- ❌ Custom punctuation rules per file
- ❌ GUI interface
- ❌ Cloud/web service
- ❌ Real-time processing
- ❌ Collaborative editing

### Future Versions
- ⏭️ Custom punctuation rule configuration
- ⏭️ Undo/redo functionality
- ⏭️ Web-based interface
- ⏭️ Support for other classic texts
- ⏭️ Advanced statistics and analysis
- ⏭️ Diff/preview mode with highlighting

---

## Success Metrics

### Functional Success
- [ ] Correctly processes all 38 Shakespeare plays
- [ ] Blocks all 4+ pure poetry files by default
- [ ] Provides accurate file type detection (≥95% confidence)
- [ ] Creates backups for 100% of processed files
- [ ] Restores permissions on 100% of read-only files

### User Success
- [ ] Human users can process files without errors
- [ ] Coding agents can integrate via JSON interface
- [ ] Documentation is clear and comprehensive
- [ ] Error messages are helpful and actionable

### Quality Success
- [ ] Zero data loss incidents
- [ ] Zero poetry files incorrectly processed
- [ ] 100% backup creation success rate
- [ ] ≥80% code coverage

---

## Risks & Mitigation

### Risk 1: Processing Poetry as Dialogue
**Impact:** High - Permanent damage to poetry
**Probability:** Medium (without file type detection)
**Mitigation:**
- Implement file type detection (FR-1)
- Block poetry processing by default (FR-4)
- Require explicit `--force` flag
- Provide clear warnings

### Risk 2: Data Loss
**Impact:** High - Lost work
**Probability:** Low (with backups)
**Mitigation:**
- Always create backups (FR-6)
- Test restore process
- Validate backup integrity

### Risk 3: Incorrect Dialogue Detection
**Impact:** Medium - Some dialogue not processed
**Probability:** Low (state machine well-tested)
**Mitigation:**
- Comprehensive test suite
- Manual validation on sample files
- Statistics reporting

### Risk 4: Permission Errors
**Impact:** Low - Processing fails
**Probability:** Medium (read-only files common)
**Mitigation:**
- Detect and handle read-only files (FR-5)
- Restore permissions even on failure
- Clear error messages

---

## Dependencies

### Runtime Dependencies
- Python 3.8+
- Standard library only:
  - `re` - Regular expressions
  - `pathlib` - File path handling
  - `stat` - File permissions
  - `subprocess` - fzf integration
  - `sys`, `os` - System operations
  - `json` - JSON output
  - `typing` - Type hints

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `mypy` - Type checking

### External Tools (Optional)
- `fzf` - Interactive file selection (optional, degrades gracefully)

---

## Acceptance Criteria

### Must Have (P0)
- [x] File type detection working
- [x] Play processing working correctly
- [x] Poetry files blocked by default
- [x] Backup creation working
- [x] Permission handling working
- [ ] JSON output implemented
- [ ] Validation mode implemented
- [ ] Exit codes standardized
- [ ] Documentation complete

### Should Have (P1)
- [ ] Dry-run mode
- [ ] Statistics counting (punctuation removed)
- [ ] Narrative poem mode
- [ ] Comprehensive error messages
- [ ] Unit test suite
- [ ] Agent usage examples

### Nice to Have (P2)
- [ ] Output directory option
- [ ] Verbose/quiet modes
- [ ] Batch statistics
- [ ] Progress indicators
- [ ] Color output

---

## Glossary

**Character Name:** Line identifying who is speaking (e.g., `HAMLET.`)

**Dialogue Line:** Text spoken by a character in a play

**Stage Direction:** Instructions for actors (e.g., `[Exit Ghost]`)

**Narrative Poem:** Poem that tells a story with quoted dialogue

**Pure Poetry:** Lyric poetry without character dialogue (sonnets, etc.)

**State Machine:** Algorithm tracking whether currently in dialogue mode

**fzf:** Fuzzy finder tool for interactive file selection

**Gutenberg:** Project Gutenberg, source of public domain texts

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | | | |
| Technical Lead | | | |
| QA Lead | | | |

---

**Document Control:**
- **Created:** 2025-10-20
- **Last Updated:** 2025-10-20
- **Version:** 1.0
- **Status:** Draft - Planning Phase
