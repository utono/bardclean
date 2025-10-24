# bardclean - Agent Usage Guide

**Version:** 1.0.0
**Purpose:** Guide for coding agents and automation scripts

This document provides comprehensive information for agents and scripts that need to integrate with `bardclean`.

---

## Quick Start for Agents

### 1. Validate Files Before Processing

**Always validate first** to check if files are safe to process:

```bash
python3 /home/mlj/utono/bardclean/bardclean.py --validate --json hamlet_gut.txt
```

**Parse the JSON output:**
```json
{
  "mode": "validation",
  "timestamp": "2025-10-20T17:00:00.000000",
  "files_validated": 1,
  "results": [
    {
      "filepath": "/path/to/hamlet_gut.txt",
      "is_shakespeare_file": true,
      "detected_type": "play",
      "confidence": 0.95,
      "is_processable": true,
      "processing_mode": "dialogue",
      "features": {
        "character_count": 378,
        "character_names": ["HAMLET", "OPHELIA", "..."],
        "stage_direction_count": 245,
        "act_scene_count": 20,
        "quoted_dialogue_count": 0,
        "roman_numeral_count": 0,
        "has_narrator_tags": false
      },
      "warnings": [],
      "recommendation": "Safe to process as play - dialogue mode recommended"
    }
  ]
}
```

### 2. Check Processability

```python
import json
import subprocess

result = subprocess.run(
    ['python3', 'bardclean.py', '--validate', '--json', 'hamlet_gut.txt'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
file_result = data['results'][0]

if file_result['is_processable']:
    print(f"✓ Safe to process: {file_result['recommendation']}")
else:
    print(f"✗ Do NOT process: {file_result['recommendation']}")
    print(f"  Warnings: {file_result['warnings']}")
```

### 3. Process Files with JSON Output

```bash
python3 bardclean.py --json hamlet_gut.txt macbeth_gut.txt
```

**JSON Response:**
```json
{
  "status": "success",
  "exit_code": 0,
  "timestamp": "2025-10-20T17:00:00.000000",
  "files_processed": 2,
  "files_failed": 0,
  "files_skipped": 0,
  "results": [
    {
      "filepath": "/path/to/hamlet_gut.txt",
      "status": "success",
      "file_type": "play",
      "confidence": 0.95,
      "total_lines": 6769,
      "modified_lines": 2341,
      "unchanged_lines": 4428
    },
    {
      "filepath": "/path/to/macbeth_gut.txt",
      "status": "success",
      "file_type": "play",
      "confidence": 0.95,
      "total_lines": 3019,
      "modified_lines": 1203,
      "unchanged_lines": 1816
    }
  ]
}
```

---

## Exit Codes

**Critical for error handling:**

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | All files processed successfully |
| 1 | General Error | Check error messages, investigate |
| 2 | File Not Found | Verify file paths are correct |
| 3 | Permission Error | Check file permissions |
| 4 | Invalid Format | Poetry file blocked (expected behavior) |
| 5 | Validation Failed | File failed validation checks |
| 6 | No Files | No files provided or selected |
| 7 | User Cancelled | User cancelled fzf selection |

**Example error handling:**

```python
result = subprocess.run(['python3', 'bardclean.py', 'sonnets_gut.txt'])

if result.returncode == 4:
    print("Poetry file blocked (correct behavior)")
elif result.returncode == 0:
    print("Success")
else:
    print(f"Error: Exit code {result.returncode}")
```

---

## JSON Schema Definitions

### ValidationResult Schema

```json
{
  "filepath": "string",              // Absolute path to file
  "is_shakespeare_file": "boolean",  // Whether file appears to be Shakespeare
  "detected_type": "string",         // play | sonnet | narrative_poem | lyric_poem | unknown
  "confidence": "number",            // 0.0-1.0 detection confidence
  "is_processable": "boolean",       // Whether safe to process
  "processing_mode": "string",       // dialogue | quoted | none
  "features": {
    "character_count": "number",     // Number of unique character names
    "character_names": ["string"],   // First 10 character names
    "stage_direction_count": "number",
    "act_scene_count": "number",
    "quoted_dialogue_count": "number",
    "roman_numeral_count": "number",
    "has_narrator_tags": "boolean"
  },
  "warnings": ["string"],            // List of warnings
  "recommendation": "string"         // Human-readable recommendation
}
```

### ProcessingResult Schema

```json
{
  "filepath": "string",              // Absolute path to file
  "status": "string",                // success | error | skipped
  "file_type": "string",             // play | sonnet | narrative_poem | lyric_poem
  "confidence": "number",            // 0.0-1.0 detection confidence
  "total_lines": "number",           // Total lines in file
  "modified_lines": "number",        // Lines modified
  "unchanged_lines": "number",       // Lines unchanged
  "backup_created": "string",        // Path to backup file (if created)
  "error_message": "string"          // Error message (if status='error' or 'skipped')
}
```

### BatchResult Schema

```json
{
  "status": "string",                // success | partial | error
  "exit_code": "number",             // Exit code (0-7)
  "timestamp": "string",             // ISO 8601 timestamp
  "files_processed": "number",       // Successfully processed count
  "files_failed": "number",          // Failed count
  "files_skipped": "number",         // Skipped count (poetry files)
  "results": [ProcessingResult]      // Array of ProcessingResult objects
}
```

---

## Agent Workflow Examples

### Workflow 1: Validate Before Processing

```python
#!/usr/bin/env python3
"""Safe Shakespeare processing workflow."""

import json
import subprocess
from pathlib import Path

def validate_and_process(filepath):
    """Validate file, then process if safe."""

    # Step 1: Validate
    validate_cmd = ['python3', 'bardclean.py', '--validate', '--json', filepath]
    result = subprocess.run(validate_cmd, capture_output=True, text=True)

    validation = json.loads(result.stdout)
    file_result = validation['results'][0]

    # Step 2: Check if processable
    if not file_result['is_processable']:
        print(f"⚠️  Skipping {Path(filepath).name}: {file_result['recommendation']}")
        for warning in file_result['warnings']:
            print(f"   {warning}")
        return False

    # Step 3: Process file
    print(f"✓ Processing {Path(filepath).name}")
    process_cmd = ['python3', 'bardclean.py', '--json', filepath]
    result = subprocess.run(process_cmd, capture_output=True, text=True)

    process_result = json.loads(result.stdout)

    if process_result['exit_code'] == 0:
        print(f"  ✓ Success: {process_result['files_processed']} file(s) processed")
        return True
    else:
        print(f"  ✗ Failed: Exit code {process_result['exit_code']}")
        return False

# Example usage
files = ['hamlet_gut.txt', 'sonnets_gut.txt', 'macbeth_gut.txt']
for file in files:
    validate_and_process(file)
```

### Workflow 2: Batch Processing with Filtering

```python
#!/usr/bin/env python3
"""Filter and process only safe files."""

import json
import subprocess

def filter_and_process_safe_files(file_list):
    """Process only files that are safe (plays)."""

    safe_files = []

    # Validate all files
    for filepath in file_list:
        validate_cmd = ['python3', 'bardclean.py', '--validate', '--json', filepath]
        result = subprocess.run(validate_cmd, capture_output=True, text=True)

        validation = json.loads(result.stdout)
        file_result = validation['results'][0]

        if file_result['is_processable'] and file_result['detected_type'] == 'play':
            safe_files.append(filepath)
            print(f"✓ {filepath}: Safe play (confidence {file_result['confidence']:.2f})")
        else:
            print(f"⊘ {filepath}: Skipped ({file_result['detected_type']})")

    # Process safe files in batch
    if safe_files:
        print(f"\nProcessing {len(safe_files)} safe files...")
        process_cmd = ['python3', 'bardclean.py', '--json'] + safe_files
        result = subprocess.run(process_cmd, capture_output=True, text=True)

        process_result = json.loads(result.stdout)
        print(f"Result: {process_result['files_processed']} processed, {process_result['files_failed']} failed")

        return process_result
    else:
        print("No safe files to process")
        return None

# Example
all_files = [
    'hamlet_gut.txt',
    'sonnets_gut.txt',        # Will be skipped (poetry)
    'macbeth_gut.txt',
    'venus_and_adonis_gut.txt'  # Will be skipped (narrative poem)
]

filter_and_process_safe_files(all_files)
```

### Workflow 3: Dry-Run Preview

```python
#!/usr/bin/env python3
"""Preview changes before applying."""

import subprocess

def preview_changes(filepath):
    """Show what would change without modifying file."""

    cmd = ['python3', 'bardclean.py', '--dry-run', filepath]
    result = subprocess.run(cmd)

    # Dry-run shows human-readable preview
    # Exit code 0 = would succeed
    # Exit code 4 = poetry blocked

    if result.returncode == 0:
        answer = input("\nApply these changes? (y/n): ")
        if answer.lower() == 'y':
            process_cmd = ['python3', 'bardclean.py', filepath]
            subprocess.run(process_cmd)

    return result.returncode

preview_changes('hamlet_gut.txt')
```

### Workflow 4: Error Handling and Retry

```python
#!/usr/bin/env python3
"""Robust error handling with retry logic."""

import json
import subprocess
import time

def process_with_retry(filepath, max_retries=3):
    """Process file with retry on transient errors."""

    for attempt in range(max_retries):
        cmd = ['python3', 'bardclean.py', '--json', filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)

        exit_code = result.returncode

        # Success
        if exit_code == 0:
            data = json.loads(result.stdout)
            print(f"✓ Success: {filepath}")
            return data

        # Expected failures (don't retry)
        elif exit_code in [2, 4, 5, 6, 7]:
            data = json.loads(result.stdout)
            print(f"✗ Cannot process {filepath}: Exit code {exit_code}")
            return data

        # Transient errors (retry)
        elif exit_code in [1, 3]:
            print(f"⚠️  Attempt {attempt + 1} failed: Exit code {exit_code}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue

    print(f"✗ Failed after {max_retries} attempts")
    return None

process_with_retry('hamlet_gut.txt')
```

---

## CLI Examples for Agents

### Validation Examples

```bash
# Single file validation
python3 bardclean.py --validate hamlet_gut.txt

# JSON validation (parseable)
python3 bardclean.py --validate --json hamlet_gut.txt

# Multiple file validation
python3 bardclean.py --validate hamlet_gut.txt macbeth_gut.txt sonnets_gut.txt

# Validation from custom directory
python3 bardclean.py --dir /path/to/texts --validate hamlet_gut.txt
```

### Processing Examples

```bash
# Process single file
python3 bardclean.py hamlet_gut.txt

# Process with JSON output
python3 bardclean.py --json hamlet_gut.txt

# Process multiple files
python3 bardclean.py hamlet_gut.txt macbeth_gut.txt

# Process with verbose output
python3 bardclean.py --verbose hamlet_gut.txt

# Process with quiet output (errors only)
python3 bardclean.py --quiet hamlet_gut.txt

# Dry-run preview
python3 bardclean.py --dry-run hamlet_gut.txt

# Skip backup creation (agents only, risky!)
python3 bardclean.py --no-backup hamlet_gut.txt

# Force process poetry (NOT recommended!)
python3 bardclean.py --force sonnets_gut.txt
```

---

## Integration Examples

### Shell Script Integration

```bash
#!/bin/bash
# Process all Shakespeare plays safely

SHAKESPEARE_DIR="$HOME/utono/literature/shakespeare-william/gutenberg"
BARDCLEAN="$HOME/utono/bardclean/bardclean.py"

# Validate all files first
echo "Validating files..."
python3 "$BARDCLEAN" --validate --json "$SHAKESPEARE_DIR"/*.txt > validation.json

# Parse JSON and extract processable files
# (This is simplified - real implementation would parse JSON properly)

# Process only safe files
echo "Processing plays..."
python3 "$BARDCLEAN" --json \
    "$SHAKESPEARE_DIR/hamlet_gut.txt" \
    "$SHAKESPEARE_DIR/macbeth_gut.txt" \
    "$SHAKESPEARE_DIR/othello_gut.txt" \
    > processing_results.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "✓ All files processed successfully"
else
    echo "✗ Some files failed - check processing_results.json"
fi
```

### Python Script Integration

```python
#!/usr/bin/env python3
"""Complete integration example."""

import json
import subprocess
import sys
from pathlib import Path

BARDCLEAN = Path.home() / "utono" / "bardclean" / "bardclean.py"
SHAKESPEARE_DIR = Path.home() / "utono" / "literature" / "shakespeare-william" / "gutenberg"

def run_bardclean(args, capture=True):
    """Run bardclean with given arguments."""
    cmd = ['python3', str(BARDCLEAN)] + args

    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    else:
        return subprocess.run(cmd)

def validate_file(filepath):
    """Validate a single file."""
    result = run_bardclean(['--validate', '--json', str(filepath)])

    if result.returncode in [0, 5]:  # Success or validation failed
        data = json.loads(result.stdout)
        return data['results'][0]
    else:
        print(f"Error validating {filepath}: Exit code {result.returncode}")
        return None

def process_file(filepath):
    """Process a single file."""
    result = run_bardclean(['--json', str(filepath)])

    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data['results'][0]
    else:
        print(f"Error processing {filepath}: Exit code {result.returncode}")
        return None

def main():
    """Main processing pipeline."""

    # Get all .txt files
    txt_files = list(SHAKESPEARE_DIR.glob("*.txt"))

    print(f"Found {len(txt_files)} files")

    # Validate all files
    safe_files = []
    for filepath in txt_files:
        validation = validate_file(filepath)

        if validation and validation['is_processable']:
            safe_files.append(filepath)
            print(f"✓ {filepath.name}: {validation['detected_type']} (confidence {validation['confidence']:.2f})")
        else:
            reason = validation['recommendation'] if validation else "Unknown error"
            print(f"⊘ {filepath.name}: {reason}")

    # Process safe files
    print(f"\nProcessing {len(safe_files)} safe files...")

    results = []
    for filepath in safe_files:
        result = process_file(filepath)
        if result:
            results.append(result)

    # Summary
    success = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - success

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total files: {len(txt_files)}")
    print(f"  Safe to process: {len(safe_files)}")
    print(f"  Successfully processed: {success}")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## Best Practices for Agents

### 1. Always Validate First

```python
# ✓ GOOD
validation = validate_file(filepath)
if validation['is_processable']:
    process_file(filepath)

# ✗ BAD
process_file(filepath)  # Might damage poetry files!
```

### 2. Use JSON Output

```python
# ✓ GOOD - Parseable, reliable
result = subprocess.run(['python3', 'bardclean.py', '--json', 'file.txt'], capture_output=True)
data = json.loads(result.stdout)

# ✗ BAD - Human output, hard to parse
result = subprocess.run(['python3', 'bardclean.py', 'file.txt'], capture_output=True)
# Now you have to parse human-readable text
```

### 3. Check Exit Codes

```python
# ✓ GOOD
result = subprocess.run(['python3', 'bardclean.py', 'file.txt'])
if result.returncode == 0:
    print("Success")
elif result.returncode == 4:
    print("Poetry file blocked (expected)")
else:
    print(f"Error: {result.returncode}")

# ✗ BAD
subprocess.run(['python3', 'bardclean.py', 'file.txt'])
# No error handling!
```

### 4. Never Use --force Automatically

```python
# ✓ GOOD
if not validation['is_processable']:
    print(f"Skipping poetry file: {filepath}")
    return

# ✗ BAD
subprocess.run(['python3', 'bardclean.py', '--force', filepath])
# This will damage poetry files!
```

### 5. Preserve Backups

```python
# ✓ GOOD - Default behavior creates backups
subprocess.run(['python3', 'bardclean.py', 'file.txt'])

# ⚠️  RISKY - Only for temporary/test files
subprocess.run(['python3', 'bardclean.py', '--no-backup', 'test_file.txt'])
```

---

## Troubleshooting

### Issue: "File detected as 'sonnet' (pure poetry)"

**Cause:** File contains Shakespeare's poetry, not dialogue
**Solution:** This is correct behavior - do NOT process poetry files
**Action:** Skip the file or inform user

### Issue: Exit code 2 (File Not Found)

**Cause:** File path is incorrect
**Solution:** Verify file exists and path is absolute
**Action:** Use `Path.resolve()` to get absolute paths

### Issue: Exit code 3 (Permission Error)

**Cause:** Cannot read/write file
**Solution:** Check file permissions
**Action:** Use `chmod` or run with appropriate permissions

### Issue: JSON output contains human-readable text

**Cause:** Not using `--json` flag
**Solution:** Always use `--json` for programmatic access
**Action:** Add `--json` to command

### Issue: Validation shows low confidence

**Cause:** File type is uncertain
**Solution:** Review file manually
**Action:** If it's truly a play, it's safe to process

---

## Summary

### Key Commands

```bash
# Validate (always first!)
python3 bardclean.py --validate --json <file>

# Process with JSON output
python3 bardclean.py --json <file>

# Preview (dry-run)
python3 bardclean.py --dry-run <file>
```

### Key Rules

1. ✅ **Always validate first** - Check `is_processable`
2. ✅ **Use JSON output** - Add `--json` flag
3. ✅ **Check exit codes** - Handle errors properly
4. ✅ **Respect poetry protection** - Don't use `--force`
5. ✅ **Keep backups** - Don't use `--no-backup` unless necessary

### File Types

- **Plays**: ✅ Safe to process
- **Narrative Poems**: ⚠️ Processable with caution
- **Sonnets**: ❌ Do NOT process
- **Lyric Poems**: ❌ Do NOT process

---

**Version:** 1.0.0
**Last Updated:** 2025-10-20
**Contact:** See README.md for project information
