# Planning Document: Shakespeare Dialogue Punctuation Processor

**Project:** Strip punctuation from Shakespeare dialogue lines
**Date Started:** 2025-10-20
**Status:** Planning & Initial Implementation Complete

---

## Table of Contents

1. [Project Genesis](#project-genesis)
2. [Initial Analysis](#initial-analysis)
3. [File Structure Discovery](#file-structure-discovery)
4. [Algorithm Design](#algorithm-design)
5. [Implementation Journey](#implementation-journey)
6. [File Type Discovery](#file-type-discovery)
7. [Coding Agent Enhancements](#coding-agent-enhancements)
8. [Implementation Phases](#implementation-phases)
9. [Technical Decisions](#technical-decisions)
10. [Testing Strategy](#testing-strategy)
11. [Future Enhancements](#future-enhancements)

---

## Project Genesis

### Initial Request
User requested to examine punctuation in Shakespeare Gutenberg files and create a plan to strip all punctuation from dialogue lines except periods (full stops).

**Initial Scope:**
- Directory: `$HOME/utono/literature/shakespeare-william/gutenberg`
- File format: Project Gutenberg Shakespeare texts
- Target: Dialogue lines only
- Preserve: Periods

### Scope Evolution
Through iterative refinement:
1. **Periods** → Added preservation
2. **Apostrophes** → Added preservation (for contractions like `'tis`)
3. **Question marks** → Added preservation (for questions)
4. **Exclamation marks** → Initially preserved, then removed
5. **File types** → Discovered need to distinguish plays from poetry

---

## Initial Analysis

### Step 1: File Discovery

**Command:**
```bash
ls -la $HOME/utono/literature/shakespeare-william/gutenberg
```

**Findings:**
- 44 total `.txt` files
- Mix of plays, poems, and sonnets
- All read-only permissions (`r--r--r--`)
- Consistent naming: `*_gut.txt`

### Step 2: Sample File Examination

**Files examined:**
1. `hamlet_gut.txt` - Play format
2. `romeo_and_juliet_gut.txt` - Play format
3. `troilus_and_cressida_gut.txt` - Play format (ALL CAPS character names)

**Initial patterns observed:**
```
Ber.                          # Character name (mixed case)
Who's there?                  # Dialogue line

Fran.                         # Character name
Nay, answer me: stand, and unfold yourself.    # Dialogue

[Enter Horatio and Marcellus.] # Stage direction
```

### Step 3: Punctuation Inventory

**Found in dialogue:**
- `,` - Commas (very common)
- `;` - Semicolons (common)
- `:` - Colons (moderate)
- `?` - Question marks (moderate)
- `!` - Exclamation marks (moderate)
- `'` - Apostrophes (very common in contractions)
- `-` - Hyphens/dashes (less common)
- `"` - Quotation marks (rare in play dialogue)

**Not found:**
- Parentheses `()` - Not used in play dialogue
- Square brackets `[]` - Used only for stage directions

---

## File Structure Discovery

### Play Structure (38 files)

**Header Section:**
```
HAMLET, PRINCE OF DENMARK

by William Shakespeare

PERSONS REPRESENTED.

Claudius, King of Denmark.
Hamlet, Son to the former, and Nephew to the present King.
...
```

**Act/Scene Structure:**
```
ACT I.

Scene I. Elsinore. A platform before the Castle.

[Francisco at his post. Enter to him Bernardo.]
```

**Character Names - Pattern 1 (Mixed Case):**
```
Ber.
Fran.
Hor.
Mar.
```

**Character Names - Pattern 2 (ALL CAPS):**
```
TROILUS.
PANDARUS.
HAMLET.
OPHELIA.
```

**Dialogue Pattern:**
```
HAMLET.
To be, or not to be: that is the question.
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles,
And by opposing end them.

[Blank line ends dialogue block]
```

**Stage Directions:**
```
[Enter HAMLET]
[Exit Ghost]
[Aside]
[They fight]
[Dies]
```

### Narrative Poem Structure (2 files)

**Files:**
- `venus_and_adonis_gut.txt`
- `rape_of_lucrece_gut.txt`

**Structure:**
```
VENUS AND ADONIS

by William Shakespeare

     EVEN as the sun with purple-colour'd face
     Had ta'en his last leave of the weeping morn,
     Rose-cheek'd Adonis tried him to the chase;
     Hunting he lov'd, but love he laugh'd to scorn;

     'Thrice fairer than myself,' thus she began,
     'The field's chief flower, sweet above compare,
```

**Key Features:**
- No character names with periods
- No stage directions
- Narrative voice + quoted dialogue
- Quoted dialogue starts with `'`
- Narrator tags: `quoth he`, `thus she began`
- Stanza structure with blank lines

**Quoted Dialogue Patterns:**
```
'Thrice fairer than myself,' thus she began,
'Vouchsafe, thou wonder, to alight thy steed,

Quoth he, 'She took me kindly by the hand,
'And how her hand, in my hand being lock'd,

Thus he replies: 'The colour in thy face,
```

### Sonnet Structure (154 sonnets in one file)

**File:** `sonnets_gut.txt`

**Structure:**
```
THE SONNETS
by William Shakespeare

I

From fairest creatures we desire increase,
That thereby beauty's rose might never die,
But as the riper should by time decease,
His tender heir might bear his memory:
...
  Pity the world, or else this glutton be,
  To eat the world's due, by the grave and thee.

II

When forty winters shall besiege thy brow,
...
```

**Key Features:**
- Roman numeral titles (I, II, III, ..., CLIV)
- 14 lines per sonnet
- Rhyme scheme: ABAB CDCD EFEF GG
- No character names
- No stage directions
- **Pure poetry - authorial voice, not dialogue**

### Lyric Poem Structure

**Files:**
- `phoenix_and_the_turtle_gut.txt`
- `passionate_pilgrim_gut.txt`
- `lovers_complaint_gut.txt`

**Structure:**
```
THE PHOENIX AND THE TURTLE

by William Shakespeare

Let the bird of loudest lay,
On the sole Arabian tree,
Herald sad and trumpet be,
To whose sound chaste wings obey.
```

**Key Features:**
- Short lyric poems
- No character names or dialogue
- May have section markers (e.g., `THRENOS.`)
- **Pure poetry - should not be processed**

---

## Algorithm Design

### State Machine Approach

**Why State Machine?**
- Dialogue detection requires context
- Need to track "currently in dialogue" vs "not in dialogue"
- Must handle multi-line dialogue blocks
- Must exit dialogue mode on blank lines or new characters

**States:**

```
┌─────────────┐
│   Initial   │ ← Not in dialogue
│   State     │
└──────┬──────┘
       │
       │ Character name detected (e.g., "HAMLET.")
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  │
┌─────────────┐                           │
│  Dialogue   │ ← Process lines           │
│    Mode     │                           │
└──────┬──────┘                           │
       │                                  │
       │ Blank line / Stage direction /  │
       │ New character name              │
       └──────────────────────────────────┘
```

**State Transitions:**

| Current State | Event | Next State | Action |
|--------------|-------|------------|--------|
| Initial | Character name | Dialogue | Skip line, enter dialogue |
| Initial | Stage direction | Initial | Skip line |
| Initial | Blank line | Initial | Skip line |
| Initial | Metadata/header | Initial | Skip line |
| Dialogue | Dialogue line | Dialogue | Process line (strip punct) |
| Dialogue | Character name | Dialogue | Skip line, stay in dialogue |
| Dialogue | Blank line | Initial | Skip line, exit dialogue |
| Dialogue | Stage direction | Initial | Skip line, exit dialogue |

### Pattern Recognition

**Character Name Detection:**

**Initial Pattern (Wrong):**
```python
CHAR_NAME_PATTERN = re.compile(r'^[A-Z][a-z]*\.$')
```
- **Problem:** Only matched mixed case (`Ber.`)
- **Missed:** ALL CAPS names (`HAMLET.`)

**Second Pattern (Wrong):**
```python
CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Z\s]*\.$')
```
- **Problem:** Only matched ALL CAPS
- **Missed:** Mixed case (`Ber.`)
- **False positive:** `ACT I.` matched

**Final Pattern (Correct):**
```python
CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]*\.$')
```
- **Matches:** Both `HAMLET.` and `Ber.` and `First Musician.`
- **Still needs:** Additional filtering for `ACT`, `SCENE`, length

**Enhanced Detection:**
```python
def is_character_name(self, line: str) -> bool:
    stripped = line.strip()

    # Must match the pattern
    if not self.CHAR_NAME_PATTERN.match(stripped):
        return False

    # Exclude common non-character patterns
    if stripped.startswith(('ACT ', 'SCENE', 'Scene ')):
        return False

    # Character names should be reasonably short (under 30 chars)
    if len(stripped) > 30:
        return False

    return True
```

**Stage Direction Detection:**

```python
STAGE_DIR_PATTERN = re.compile(r'^\[.*\]$')
```
- Simple and accurate
- Matches: `[Enter HAMLET]`, `[Exit]`, `[Aside]`
- No false positives found

**Metadata Detection:**

```python
def is_metadata_or_header(self, line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False

    # All caps lines (titles, scene headers)
    if stripped.isupper() and len(stripped) > 1:
        return True

    # Scene/Act markers
    if stripped.startswith(('ACT ', 'SCENE', 'Scene ', 'PROLOGUE', 'EPILOGUE')):
        return True

    # Cast list lines (Name, description)
    if ', ' in stripped and not self.in_dialogue:
        return True

    return False
```

**Punctuation Removal:**

**Final Pattern:**
```python
PUNCT_PATTERN = re.compile(r"[,;:!\"\-—–]")
```

**Evolution:**
1. Initial: `[,;:!?'\"\-—–]` - Removed everything
2. User: Keep apostrophes → `[,;:!?\"\-—–]`
3. User: Keep question marks → `[,;:!\"\-—–]`
4. User: Keep exclamations → `[,;:\"\-—–]`
5. User: Remove exclamations → `[,;:!\"\-—–]` (final)

---

## Implementation Journey

### Version 1: Basic Script

**Created:** `strip_dialogue_punctuation.py`

**Features:**
- DialogueProcessor class
- State machine for dialogue detection
- Pattern matching for character names
- Punctuation removal
- Interactive fzf selection
- Command-line file arguments

**Test Results:**
```bash
# Test on sample file
Total lines: 28
Lines modified: 5
Lines unchanged: 23
```

### Version 2: Permission Handling

**Problem Discovered:**
```
Error writing troilus_and_cressida_gut.txt: [Errno 13] Permission denied
```

**Root Cause:** Files are read-only (`r--r--r--`)

**Solution Implemented:**
```python
# Store original permissions
original_mode = os.stat(self.filepath).st_mode

# Make writable temporarily
if not (original_mode & stat.S_IWUSR):
    os.chmod(self.filepath, original_mode | stat.S_IWUSR)

# Process file...

# Restore original permissions
os.chmod(self.filepath, original_mode)
```

**Also:**
- Apply same permissions to backup
- Restore permissions even on error

### Version 3: Improved Character Detection

**Problem Discovered:**
```bash
# Processing troilus_and_cressida_gut.txt
Total lines: 6301
Lines modified: 3        # Way too low!
Lines unchanged: 6298
```

**Root Cause:** Character names in ALL CAPS not detected

**Solution:** Updated regex pattern (see Pattern Recognition section above)

**Test Results After Fix:**
```bash
Total lines: 6301
Lines modified: 2076     # Much better!
Lines unchanged: 4225
```

### Version 4: Punctuation Refinement

**User Feedback Loop:**
1. "Retain apostrophes" → Updated pattern
2. "Retain question marks" → Updated pattern
3. "Retain exclamation marks" → Updated pattern
4. "Remove exclamation marks" → Updated pattern (final)

**Current Pattern:**
```python
PUNCT_PATTERN = re.compile(r"[,;:!\"\-—–]")
```

**Preserves:** `.` `?` `'`
**Removes:** `,` `;` `:` `!` `"` `-` `—` `–`

---

## File Type Discovery

### Critical Realization

**Question:** Should the script process `sonnets_gut.txt`?

**Analysis:**
- Sonnets are **authorial poetry**, not character dialogue
- Processing would strip punctuation from Shakespeare's poems
- This would be **destructive and incorrect**

**Implication:** Need file type detection to prevent processing poetry!

### File Type Classification

**Research Phase:**

Examined 4 file categories:
1. ✅ **Plays** (38 files) - Safe to process
2. ⚠️ **Narrative poems** (2 files) - Has dialogue but embedded in poetry
3. ❌ **Sonnets** (1 file, 154 sonnets) - Pure poetry, no dialogue
4. ❌ **Lyric poems** (3+ files) - Pure poetry, no dialogue

### Detection Algorithm Design

**Play Detection:**
```python
has_character_names = bool(re.search(r'^[A-Z][A-Z\s]+\.$', content, re.MULTILINE))
has_stage_directions = bool(re.search(r'^\[.*\]$', content, re.MULTILINE))
has_act_scene = bool(re.search(r'^(ACT|SCENE)', content, re.MULTILINE))

if has_character_names and has_stage_directions:
    return 'play'
```

**Sonnet Detection:**
```python
has_sonnets = bool(re.search(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X)$', content, re.MULTILINE))

if has_sonnets and not has_character_names:
    return 'sonnet'
```

**Narrative Poem Detection:**
```python
has_quoted_dialogue = bool(re.search(r"^     '[A-Z]", content, re.MULTILINE))
has_narrator_tags = bool(re.search(r"(quoth|thus she|thus he)", content, re.IGNORECASE))

if has_quoted_dialogue and has_narrator_tags:
    return 'narrative_poem'
```

**Lyric Poem Detection:**
```python
if not has_character_names and not has_stage_directions:
    return 'lyric_poem'
```

### File Inventory by Type

**Plays (38 files):**
```
hamlet_gut.txt
macbeth_gut.txt
othello_gut.txt
lear_gut.txt
romeo_and_juliet_gut.txt
julius_caesar_gut.txt
troilus_and_cressida_gut.txt
antony_and_cleopatra_gut.txt
coriolanus_gut.txt
henry_iv_part_1_gut.txt
henry_iv_part_2_gut.txt
henry_v_gut.txt
henry_vi_part_1_gut.txt
henry_vi_part_2_gut.txt
henry_vi_part_3_gut.txt
henry_viii_gut.txt
richard_ii_gut.txt
richard_iii_gut.txt
john_gut.txt
merchant_of_venice_gut.txt
merry_wives_of_windsor_gut.txt
much_ado_about_nothing_gut.txt
loves_labours_lost_gut.txt
alls_well_that_ends_well_gut.txt
as_you_like_it_gut.txt
comedy_of_errors_gut.txt
cymbeline_gut.txt
measure_for_measure_gut.txt
midsummer_nights_dream_gut.txt
pericles_gut.txt
taming_of_the_shrew_gut.txt
tempest_gut.txt
timon_of_athens_gut.txt
tragedy_of_titus_andronicus_gut.txt
twelfth_night_gut.txt
two_gentlemen_of_verona_gut.txt
winters_tale_gut.txt
the_two_noble_kinsmen.txt
```

**Narrative Poems (2 files):**
```
venus_and_adonis_gut.txt
rape_of_lucrece_gut.txt
```

**Sonnets (1 file):**
```
sonnets_gut.txt
```

**Lyric Poems (3+ files):**
```
phoenix_and_the_turtle_gut.txt
passionate_pilgrim_gut.txt
lovers_complaint_gut.txt
```

---

## Coding Agent Enhancements

### Motivation

**Problem:** Coding agents need:
- Structured, machine-readable output
- Safe batch processing
- File type validation
- Predictable error handling

### Solution Design

**Key Features for Agents:**

1. **JSON Output** - Structured data instead of human text
2. **Validation Mode** - Check files before processing
3. **Dry-Run Mode** - Preview changes without modification
4. **File Type Detection** - Automatic classification
5. **Exit Codes** - Standard error signaling
6. **No Interactive Prompts** - Fully automatable

### JSON Output Schema

**Success Response:**
```json
{
  "status": "success",
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
        "confidence": 0.99
      },
      "processing": {
        "total_lines": 6301,
        "modified_lines": 2076
      },
      "changes": {
        "punctuation_removed": {
          "commas": 1234,
          "semicolons": 456
        }
      }
    }
  ]
}
```

**Error Response:**
```json
{
  "status": "error",
  "exit_code": 4,
  "error": {
    "type": "InvalidFileFormat",
    "message": "File detected as 'sonnet' (pure poetry)",
    "file": "sonnets_gut.txt"
  }
}
```

### Validation Mode Output

```json
{
  "file": "hamlet_gut.txt",
  "validation": {
    "is_shakespeare_file": true,
    "detected_type": "play",
    "confidence": 0.99,
    "is_processable": true,
    "features": {
      "character_names": 34,
      "stage_directions": 245
    },
    "recommendation": "Safe to process as play"
  }
}
```

### Agent Workflow Example

```python
import subprocess
import json

# Step 1: Validate all files
result = subprocess.run(
    ['python', 'strip_dialogue_punctuation.py', '--validate', '--json', '*.txt'],
    capture_output=True,
    text=True
)

validation = json.loads(result.stdout)

# Step 2: Filter processable files
plays = [f for f in validation['results']
         if f['validation']['detected_type'] == 'play']

# Step 3: Process plays only
if plays:
    files = [f['file'] for f in plays]
    result = subprocess.run(
        ['python', 'strip_dialogue_punctuation.py', '--json', '--no-backup'] + files,
        capture_output=True,
        text=True
    )

    output = json.loads(result.stdout)

    if output['status'] == 'success':
        print(f"Processed {output['files_processed']} files")
    else:
        print(f"Error: {output['error']['message']}")
```

### Exit Code Strategy

**Standard Exit Codes:**

```python
class ExitCode:
    SUCCESS = 0
    GENERAL_ERROR = 1
    FILE_NOT_FOUND = 2
    PERMISSION_ERROR = 3
    INVALID_FORMAT = 4
    VALIDATION_FAILED = 5
    NO_FILES = 6
    USER_CANCELLED = 7
```

**Agent Usage:**
```python
result = subprocess.run([...])

if result.returncode == 0:
    # Success - process results
    pass
elif result.returncode == 4:
    # File type not processable - expected for poetry
    log("Skipped poetry file")
elif result.returncode == 3:
    # Permission error - needs attention
    alert("Permission denied")
```

---

## Implementation Phases

### Phase 1: Essential for Agents (Critical)

**Priority:** P0

**Features:**
1. ✅ `--json` flag for structured output
2. ✅ `--dry-run` flag for preview
3. ✅ `--validate` flag for structure checking
4. ✅ Implement proper exit codes
5. ✅ Create `shakespeare_file_structure.md`

**Status:** Planned (not yet implemented)

**Implementation Notes:**
```python
# Add to ArgumentParser
parser.add_argument('--json', action='store_true',
                   help='Output results as JSON')
parser.add_argument('--dry-run', action='store_true',
                   help='Preview changes without modifying files')
parser.add_argument('--validate', action='store_true',
                   help='Validate file structure and type')

# Modify main() to check flags
if args.json:
    output_json(results)
else:
    output_human(results)

if args.dry_run:
    processor.dry_run = True

if args.validate:
    return validate_files(args.files)
```

### Phase 2: Enhanced Functionality

**Priority:** P1

**Features:**
6. ✅ `--no-backup` flag
7. ✅ `--stats-only` flag
8. ✅ `--output-dir` flag
9. ✅ Create `agent_usage.md`
10. ✅ Add detailed punctuation counting

**Status:** Planned

**Implementation Notes:**
```python
# Track punctuation statistics
class PunctuationStats:
    def __init__(self):
        self.commas = 0
        self.semicolons = 0
        self.colons = 0
        self.exclamations = 0
        self.quotes = 0
        self.dashes = 0

    def count(self, original, modified):
        for char in original:
            if char == ',': self.commas += 1
            elif char == ';': self.semicolons += 1
            # ...
```

### Phase 3: Library Interface

**Priority:** P2

**Features:**
11. ✅ Refactor for importable module
12. ✅ Add programmatic API
13. ✅ Add unit tests
14. ✅ Add type hints throughout

**Status:** Planned

**Implementation Notes:**
```python
# Make importable
from strip_dialogue_punctuation import (
    DialogueProcessor,
    validate_file,
    ProcessingResult
)

# Use programmatically
processor = DialogueProcessor("hamlet.txt")
result = processor.process_file(dry_run=True)
print(result.to_json())
```

---

## Technical Decisions

### Decision 1: State Machine vs Line-by-Line

**Options:**
1. State machine (track dialogue mode)
2. Line-by-line heuristics (process each line independently)

**Decision:** State machine

**Rationale:**
- More accurate dialogue detection
- Handles multi-line dialogue blocks
- Can track context
- Easier to reason about

**Trade-offs:**
- Slightly more complex
- Requires careful state management

### Decision 2: Regex vs String Methods

**Options:**
1. Regular expressions
2. String methods (`startswith`, `in`, etc.)

**Decision:** Both - Regex for patterns, string methods for simple checks

**Rationale:**
- Regex: Powerful for pattern matching (character names, stage directions)
- String methods: Faster and clearer for simple checks (startswith 'ACT')

**Example:**
```python
# Regex for complex patterns
CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]*\.$')

# String methods for simple checks
if stripped.startswith(('ACT ', 'SCENE')):
    return False
```

### Decision 3: In-Place vs Output Directory

**Options:**
1. Modify files in-place (with backup)
2. Write to output directory

**Decision:** In-place with backup (default), output directory (optional)

**Rationale:**
- In-place: Simpler user experience, preserves file locations
- Backup: Safety net for recovery
- Output directory: Useful for agents/pipelines (Phase 2 feature)

### Decision 4: Python vs Shell Script

**Options:**
1. Python script
2. Bash/sed script

**Decision:** Python

**Rationale:**
- Better state management
- More readable
- Easier testing
- Cross-platform
- Better error handling
- Can be imported as library

**Trade-offs:**
- Slightly slower than sed
- Requires Python 3.8+

### Decision 5: fzf Optional vs Required

**Options:**
1. Require fzf installation
2. Make fzf optional

**Decision:** Optional - degrade gracefully

**Rationale:**
- Not all users have fzf
- Command-line arguments work without fzf
- Better user experience

**Implementation:**
```python
try:
    result = subprocess.run(['fzf', ...], ...)
except FileNotFoundError:
    print("Error: fzf not found. Please install fzf or provide file arguments.")
    return []
```

### Decision 6: Block Poetry vs Warn Only

**Options:**
1. Block poetry processing by default
2. Warn but allow processing

**Decision:** Block by default, require `--force`

**Rationale:**
- Processing poetry is almost certainly a mistake
- Damage would be permanent (even with backup, user might not restore)
- Explicit `--force` flag makes intent clear
- Protects users from accidents

**Implementation:**
```python
if file_type in ['sonnet', 'lyric_poem'] and not args.force:
    print(f"Error: File detected as '{file_type}' (pure poetry).")
    print("Use --force to override (not recommended).")
    return False
```

### Decision 7: Single Class vs Multiple Classes

**Options:**
1. Single `DialogueProcessor` class
2. Multiple classes: `PlayProcessor`, `PoemProcessor`, `Validator`

**Decision:** Single class for now, refactor in Phase 3

**Rationale:**
- YAGNI (You Aren't Gonna Need It) - keep it simple
- Easy to refactor later
- Most processing logic is shared

**Future Refactoring (Phase 3):**
```python
class BaseProcessor:
    def process_line(self, line): ...

class PlayProcessor(BaseProcessor):
    def is_character_name(self, line): ...

class NarrativePoemProcessor(BaseProcessor):
    def is_quoted_dialogue(self, line): ...
```

---

## Testing Strategy

### Unit Tests

**Test Coverage Goals:**
- Pattern matching: 100%
- State transitions: 100%
- File operations: 90%
- Edge cases: 80%

**Test Cases:**

```python
def test_character_name_detection():
    """Test character name pattern matching."""
    assert is_character_name("HAMLET.")
    assert is_character_name("Ber.")
    assert is_character_name("First Musician.")
    assert not is_character_name("ACT I.")
    assert not is_character_name("SCENE II.")

def test_stage_direction_detection():
    """Test stage direction pattern matching."""
    assert is_stage_direction("[Enter HAMLET]")
    assert is_stage_direction("[Exit]")
    assert not is_stage_direction("(aside)")

def test_punctuation_removal():
    """Test punctuation stripping."""
    assert strip_punct("Hello, world!") == "Hello world"
    assert strip_punct("Who's there?") == "Who's there?"
    assert strip_punct("I'll go.") == "I'll go."

def test_state_transitions():
    """Test dialogue mode state machine."""
    processor = DialogueProcessor("test.txt")

    # Character name -> enter dialogue
    processor.process_line("HAMLET.")
    assert processor.in_dialogue == True

    # Blank line -> exit dialogue
    processor.process_line("")
    assert processor.in_dialogue == False
```

### Integration Tests

**Test Files:**

Create minimal test files for each type:

```
test_play.txt         # Minimal play structure
test_narrative.txt    # Minimal narrative poem
test_sonnet.txt       # Minimal sonnet
test_lyric.txt        # Minimal lyric poem
```

**Test Cases:**

```python
def test_play_processing():
    """Test full play processing."""
    processor = DialogueProcessor("test_play.txt")
    result = processor.process_file()

    assert result.success == True
    assert result.lines_modified > 0
    assert result.file_type == "play"

def test_sonnet_blocking():
    """Test that sonnets are blocked."""
    processor = DialogueProcessor("test_sonnet.txt")
    result = processor.process_file(force=False)

    assert result.success == False
    assert result.error_type == "InvalidFileFormat"
```

### Manual Validation

**Sample Files:**
- `hamlet_gut.txt` - Large play, mixed character names
- `troilus_and_cressida_gut.txt` - ALL CAPS character names
- `venus_and_adonis_gut.txt` - Narrative poem
- `sonnets_gut.txt` - Pure poetry

**Validation Checks:**
1. Compare line counts before/after
2. Spot check dialogue lines
3. Verify stage directions unchanged
4. Verify metadata unchanged
5. Confirm backup created
6. Confirm permissions restored

---

## Future Enhancements

### Phase 4: Advanced Features

**Custom Punctuation Rules:**
```python
# Config file: .punct_rules.json
{
  "remove": [",", ";", ":", "!"],
  "preserve": [".", "?", "'"],
  "files": {
    "hamlet.txt": {
      "remove": [",", ";"],  # Override for specific file
      "preserve": [".", "?", "'", "!"]
    }
  }
}
```

**Undo/Redo:**
```python
# Track changes for undo
class ChangeTracker:
    def __init__(self):
        self.history = []

    def record(self, filepath, original, modified):
        self.history.append({
            'file': filepath,
            'original': original,
            'modified': modified,
            'timestamp': datetime.now()
        })

    def undo(self, filepath):
        # Restore from history
        pass
```

**Web Interface:**
```python
# Flask app for web-based processing
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # Process and return result

@app.route('/preview', methods=['POST'])
def preview():
    # Dry-run preview
    pass
```

### Phase 5: Analytics

**Statistics Dashboard:**
```python
class Statistics:
    def analyze_corpus(self, files):
        """Analyze multiple files for patterns."""
        return {
            'total_dialogue_lines': 15000,
            'avg_punctuation_per_line': 2.3,
            'most_common_punct': ',',
            'character_dialogue_distribution': {
                'HAMLET': 1500,
                'OPHELIA': 500
            }
        }
```

**Diff Visualization:**
```python
def generate_diff_html(original, modified):
    """Generate HTML diff with highlighting."""
    return f"""
    <div class="diff">
        <div class="original">{original}</div>
        <div class="modified">{modified}</div>
        <div class="changes">
            Removed: {removed_chars}
        </div>
    </div>
    """
```

### Phase 6: Extended Format Support

**Other Classic Texts:**
- Extend to other playwrights (Marlowe, Jonson)
- Support different file formats (markdown, HTML)
- Handle different encoding schemes

**Modern Formats:**
- EPUB support
- PDF extraction
- TEI XML support

---

## Open Questions

### Question 1: Narrative Poem Processing

**Issue:** Narrative poems contain dialogue but embedded in verse

**Options:**
1. Process quoted dialogue only
2. Don't process at all
3. Let user decide

**Current Status:** Planned for Phase 2, with warnings

**Decision Needed:** User confirmation workflow?

### Question 2: Statistics Granularity

**Issue:** How detailed should punctuation statistics be?

**Options:**
1. Just total count
2. Per-punctuation-type count
3. Per-character count (HAMLET removed 50 commas)
4. Per-line analysis

**Current Status:** Phase 2 - per-punctuation-type

**Decision Needed:** Is per-character worth the complexity?

### Question 3: Output Directory Structure

**Issue:** Where to write files with `--output-dir`?

**Options:**
1. Flat: `output/hamlet.txt`
2. Preserve structure: `output/shakespeare-william/gutenberg/hamlet.txt`
3. Configurable

**Current Status:** Phase 2 feature, not yet decided

### Question 4: Library API Design

**Issue:** What should the programmatic API look like?

**Options:**
1. Functional: `process_file(path, options)`
2. Object-oriented: `DialogueProcessor(path).process()`
3. Both

**Current Status:** Phase 3, leaning toward both

---

## Lessons Learned

### Lesson 1: File Type Matters

**What Happened:** Initially designed for plays only, then discovered poetry files

**Impact:** Major design change required

**Takeaway:** Always examine full dataset before designing algorithm

### Lesson 2: Read-Only Files Are Common

**What Happened:** Script failed on first real file due to permissions

**Impact:** Had to add permission handling

**Takeaway:** Test with realistic file permissions early

### Lesson 3: Pattern Variations Are Unpredictable

**What Happened:** Character names came in both mixed case and ALL CAPS

**Impact:** Multiple pattern refinements

**Takeaway:** Examine multiple sample files, not just one

### Lesson 4: User Requirements Evolve

**What Happened:** Punctuation rules changed 4 times through feedback

**Impact:** Multiple pattern updates

**Takeaway:** Make punctuation rules configurable (future enhancement)

### Lesson 5: Coding Agents Need Different Interface

**What Happened:** Realized human-friendly output isn't agent-friendly

**Impact:** Designed JSON output mode

**Takeaway:** Consider both human and programmatic use from start

---

## References

### Documentation
- `PRD.md` - Product Requirements Document (this file's companion)
- `shakespeare_file_structure.md` - File structure reference (to be created)
- `agent_usage.md` - Agent integration guide (to be created)

### External Resources
- Project Gutenberg: https://www.gutenberg.org/
- Shakespeare's complete works
- fzf: https://github.com/junegunn/fzf

### Related Files
- `strip_dialogue_punctuation.py` - Main implementation
- Test files in `tests/` directory (to be created)
- Example files in `examples/` directory (to be created)

---

## Appendix: Command Reference

### Current Commands

```bash
# Interactive selection
python strip_dialogue_punctuation.py

# Process specific files
python strip_dialogue_punctuation.py hamlet.txt macbeth.txt

# Process all plays
python strip_dialogue_punctuation.py *_gut.txt
```

### Planned Commands (Phase 1-2)

```bash
# Validate files
python strip_dialogue_punctuation.py --validate --json *.txt

# Dry run
python strip_dialogue_punctuation.py --dry-run hamlet.txt

# Agent mode
python strip_dialogue_punctuation.py --json --no-backup hamlet.txt

# Stats only
python strip_dialogue_punctuation.py --stats-only hamlet.txt

# Output directory
python strip_dialogue_punctuation.py --output-dir ./processed *.txt

# Force poetry processing
python strip_dialogue_punctuation.py --force sonnets.txt
```

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-20 | 1.0 | Initial planning document created |

---

**End of Planning Document**
