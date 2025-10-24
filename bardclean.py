#!/usr/bin/env python3
"""
bardclean - Strip punctuation from Shakespeare dialogue lines

This script processes Shakespeare play text files and removes specific punctuation
from dialogue lines while preserving periods, question marks, and apostrophes.
It uses a state machine to intelligently detect dialogue vs non-dialogue content.

Usage:
    # Interactive selection with fzf (from default directory)
    bardclean

    # Process specific files
    bardclean file1.txt file2.txt

    # Interactive selection from custom directory
    bardclean --dir /path/to/shakespeare/texts

    # Process specific files from custom directory
    bardclean --dir /path/to/texts file1.txt file2.txt
"""

import sys
import re
import os
import stat
import subprocess
import argparse
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


class ExitCode:
    """Standard exit codes for bardclean.

    These codes enable reliable error handling by scripts and coding agents.
    """
    SUCCESS = 0                # All files processed successfully
    GENERAL_ERROR = 1          # Unspecified error occurred
    FILE_NOT_FOUND = 2         # Input file doesn't exist
    PERMISSION_ERROR = 3       # Cannot read/write file
    INVALID_FORMAT = 4         # File is not processable Shakespeare text (poetry)
    VALIDATION_FAILED = 5      # File failed validation checks
    NO_FILES = 6               # Empty file list
    USER_CANCELLED = 7         # Interactive selection cancelled


@dataclass
class FileTypeFeatures:
    """Features extracted from a Shakespeare text file for type detection.

    This dataclass stores structural features that help identify whether a file
    is a play, sonnet, narrative poem, or lyric poem.

    Attributes:
        character_names: List of unique character names found (e.g., ['HAMLET', 'OPHELIA'])
        stage_direction_count: Number of stage directions found (e.g., [Enter HAMLET])
        act_scene_count: Number of ACT/SCENE markers found
        quoted_dialogue_count: Number of lines with quoted dialogue (narrative poems)
        roman_numeral_markers: List of Roman numeral section markers (sonnets)
        has_narrator_tags: Whether narrator tags like 'quoth' or 'thus she' were found
    """
    character_names: List[str]
    stage_direction_count: int
    act_scene_count: int
    quoted_dialogue_count: int
    roman_numeral_markers: List[str]
    has_narrator_tags: bool


@dataclass
class ProcessingResult:
    """Result of processing a single file.

    Used for JSON output and programmatic access to processing results.
    """
    filepath: str
    status: str  # 'success', 'error', 'skipped'
    file_type: Optional[str] = None
    confidence: Optional[float] = None
    total_lines: int = 0
    modified_lines: int = 0
    unchanged_lines: int = 0
    backup_created: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class BatchResult:
    """Result of processing multiple files.

    Used for JSON output in batch processing mode.
    """
    status: str  # 'success', 'partial', 'error'
    exit_code: int
    timestamp: str
    files_processed: int
    files_failed: int
    files_skipped: int
    results: List[ProcessingResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'status': self.status,
            'exit_code': self.exit_code,
            'timestamp': self.timestamp,
            'files_processed': self.files_processed,
            'files_failed': self.files_failed,
            'files_skipped': self.files_skipped,
            'results': [r.to_dict() for r in self.results]
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ValidationResult:
    """Result of validating a Shakespeare text file.

    Provides file type detection, processability assessment, and recommendations
    without actually modifying the file. Critical for agent workflows.

    Attributes:
        filepath: Path to the file being validated
        is_shakespeare_file: Whether file appears to be Shakespeare text
        detected_type: File type ('play', 'sonnet', 'narrative_poem', 'lyric_poem', 'unknown')
        confidence: Detection confidence score (0.0-1.0)
        is_processable: Whether file is safe to process
        processing_mode: Recommended mode ('dialogue', 'quoted', 'none')
        features: Extracted file type features
        warnings: List of warning messages
        recommendation: Human-readable recommendation text
    """
    filepath: str
    is_shakespeare_file: bool
    detected_type: str
    confidence: float
    is_processable: bool
    processing_mode: str  # 'dialogue', 'quoted', 'none'
    features: FileTypeFeatures
    warnings: List[str]
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'filepath': self.filepath,
            'is_shakespeare_file': self.is_shakespeare_file,
            'detected_type': self.detected_type,
            'confidence': self.confidence,
            'is_processable': self.is_processable,
            'processing_mode': self.processing_mode,
            'features': {
                'character_count': len(self.features.character_names),
                'character_names': self.features.character_names[:10],  # First 10
                'stage_direction_count': self.features.stage_direction_count,
                'act_scene_count': self.features.act_scene_count,
                'quoted_dialogue_count': self.features.quoted_dialogue_count,
                'roman_numeral_count': len(self.features.roman_numeral_markers),
                'has_narrator_tags': self.features.has_narrator_tags
            },
            'warnings': self.warnings,
            'recommendation': self.recommendation
        }


class DialogueProcessor:
    """Process Shakespeare text files to strip punctuation from dialogue.

    Uses a state machine to intelligently detect dialogue vs non-dialogue content:

    State Machine:
        Initial State: Not in dialogue mode
            - Character name detected → Enter dialogue mode
            - Other content → Stay in Initial State

        Dialogue State: Processing dialogue lines
            - Blank line detected → Exit to Initial State
            - Stage direction detected → Exit to Initial State
            - Dialogue line → Process and remove punctuation
            - Character name → Start new dialogue block (stay in Dialogue State)

    Transitions:
        Enter Dialogue: When a character name pattern is detected (e.g., "HAMLET.")
        Exit Dialogue: When blank line or stage direction is encountered
        Stay in Dialogue: When processing normal dialogue lines

    The state machine ensures that only character dialogue is processed, while
    preserving stage directions, scene headers, and Shakespeare's authorial text.
    """

    # Punctuation to remove (everything except period, apostrophe, and question mark)
    # Exclamation marks are removed mid-line but preserved at line endings
    PUNCT_PATTERN = re.compile(r"[,;:!\"\-—–]")

    # Character name pattern: all caps or mixed case, short line, optionally ends with period
    # Matches: TROILUS., Ber., PANDARUS., AJAX., EGEUS, THESEUS, etc.
    CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]*\.?$')

    # Character name with inline dialogue pattern
    # Matches: "YORK. Farewell, my lord;" or "Ber. Come on,"
    CHAR_NAME_INLINE_PATTERN = re.compile(r'^([A-Z][A-Za-z\s]*\.\s+)(.+)$')

    # Stage direction pattern: enclosed in brackets
    STAGE_DIR_PATTERN = re.compile(r'^\[.*\]$')

    def __init__(self, filepath: str, force: bool = False, quiet: bool = False, dry_run: bool = False, verbose: bool = False):
        self.filepath = Path(filepath)
        self.in_dialogue = False
        self.lines_processed = 0
        self.lines_modified = 0
        self.dialogue_lines_processed = 0  # Lines processed in dialogue mode
        self.non_dialogue_lines_skipped = 0  # Lines skipped (metadata, stage directions, etc.)
        self.file_type = 'unknown'
        self.confidence = 0.0
        self.force = force
        self.quiet = quiet
        self.dry_run = dry_run
        self.verbose = verbose
        self.preview_changes = []  # List of (line_num, original, modified) for dry-run
        self.punctuation_removed = {
            'commas': 0,
            'semicolons': 0,
            'colons': 0,
            'quotes': 0,
            'dashes': 0
        }

    def is_character_name(self, line: str) -> bool:
        """Check if line is a character name."""
        stripped = line.strip()

        # Must match the pattern
        if not self.CHAR_NAME_PATTERN.match(stripped):
            return False

        # Exclude common non-character patterns
        if stripped.startswith(('ACT ', 'SCENE', 'Scene ')):
            return False

        # Exclude cast list headers
        if 'Persons' in stripped or 'Represented' in stripped or 'DRAMATIS' in stripped:
            return False

        # Character names should be reasonably short (under 30 chars)
        if len(stripped) > 30:
            return False

        return True

    def has_inline_dialogue(self, line: str) -> tuple:
        """Check if line has character name with inline dialogue.

        Returns (has_inline, char_name, dialogue) tuple.
        If has_inline is True, char_name and dialogue are the extracted parts.
        """
        stripped = line.strip()
        match = self.CHAR_NAME_INLINE_PATTERN.match(stripped)

        if not match:
            return (False, None, None)

        char_name = match.group(1).strip()
        dialogue = match.group(2).strip()

        # Exclude common non-character patterns
        if char_name.startswith(('ACT ', 'SCENE', 'Scene ')):
            return (False, None, None)

        # Character name part should be reasonably short (under 30 chars)
        if len(char_name) > 30:
            return (False, None, None)

        # Dialogue part should exist and be substantial
        if not dialogue or len(dialogue) < 3:
            return (False, None, None)

        return (True, char_name, dialogue)

    def is_stage_direction(self, line: str) -> bool:
        """Check if line is a stage direction."""
        stripped = line.strip()
        return bool(self.STAGE_DIR_PATTERN.match(stripped))

    def is_blank_or_whitespace(self, line: str) -> bool:
        """Check if line is blank or only whitespace."""
        return len(line.strip()) == 0

    def is_metadata_or_header(self, line: str) -> bool:
        """Check if line is likely metadata (all caps, scene headers, etc.)."""
        stripped = line.strip()
        if not stripped:
            return False

        # All caps lines (titles, scene headers)
        # But exclude short single-word lines (likely character names like "YORK", "HAMLET")
        if stripped.isupper() and len(stripped) > 1:
            # If it's a single word and reasonably short, it's likely a character name
            if ' ' not in stripped and len(stripped) <= 20:
                return False  # Not metadata - likely a character name
            return True  # Longer or multi-word all-caps line is metadata

        # Scene/Act markers
        if stripped.startswith(('ACT ', 'SCENE', 'Scene ', 'PROLOGUE', 'EPILOGUE')):
            return True

        # Cast list lines (Name, description)
        if ', ' in stripped and not self.in_dialogue:
            return True

        return False

    def strip_punctuation(self, line: str) -> Tuple[str, bool]:
        """
        Strip punctuation from line, preserving periods, question marks, and whitespace.
        Exclamation marks, semicolons, colons, and double-hyphens are preserved at line endings.

        Punctuation is replaced with space to prevent word concatenation,
        then multiple consecutive spaces are collapsed to single space.

        Returns (modified_line, was_modified).
        """
        original = line

        # Check what punctuation the line ends with (preserve trailing whitespace position)
        stripped = line.rstrip()
        ending_punct = None
        if stripped.endswith('!'):
            ending_punct = '!'
        elif stripped.endswith(';'):
            ending_punct = ';'
        elif stripped.endswith(':'):
            ending_punct = ':'
        elif stripped.endswith('--'):
            ending_punct = '--'
        elif stripped.endswith('—'):
            ending_punct = '—'
        elif stripped.endswith('–'):
            ending_punct = '–'

        # Count each punctuation type before removing
        self.punctuation_removed['commas'] += line.count(',')
        self.punctuation_removed['semicolons'] += line.count(';')
        self.punctuation_removed['colons'] += line.count(':')
        self.punctuation_removed['quotes'] += line.count('"')
        self.punctuation_removed['dashes'] += line.count('-') + line.count('—') + line.count('–')

        # Replace punctuation with space to prevent word concatenation
        modified = self.PUNCT_PATTERN.sub(' ', line)

        # Collapse multiple consecutive spaces to single space
        # This handles cases like "hello ! world" → "hello  world" → "hello world"
        modified = re.sub(r' {2,}', ' ', modified)

        # If original line ended with special punctuation, restore it at the end
        if ending_punct:
            # Remove the space(s) that replaced the final punctuation and add it back
            modified = modified.rstrip() + ending_punct
            # Preserve original trailing whitespace
            trailing_whitespace = line[len(line.rstrip()):]
            modified += trailing_whitespace

        return modified, (original != modified)

    def extract_features(self, content: str) -> FileTypeFeatures:
        """
        Extract structural features from file content for type detection.

        Scans the entire file content and identifies key structural elements
        that distinguish different Shakespeare file types.

        Args:
            content: Complete file content as string

        Returns:
            FileTypeFeatures object with extracted feature counts and lists
        """
        character_names = []
        stage_direction_count = 0
        act_scene_count = 0
        quoted_dialogue_count = 0
        roman_numeral_markers = []
        has_narrator_tags = False

        for line in content.split('\n'):
            stripped = line.strip()

            # Character names (e.g., "HAMLET.", "Ber.")
            if self.is_character_name(stripped):
                if stripped not in character_names:
                    character_names.append(stripped)

            # Stage directions (e.g., "[Enter HAMLET]")
            if self.is_stage_direction(stripped):
                stage_direction_count += 1

            # ACT/SCENE markers
            if re.match(r'^(ACT|SCENE)', stripped):
                act_scene_count += 1

            # Quoted dialogue - narrative poems (e.g., "'Thrice fairer than myself,'")
            if re.match(r"^\s*'[A-Z]", line):  # Use original line to preserve indentation
                quoted_dialogue_count += 1

            # Roman numerals - sonnets (e.g., "I", "II", "III", etc.)
            # Extended pattern to catch more Roman numerals
            if re.match(r'^(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|'
                       r'XVI|XVII|XVIII|XIX|XX|XXX|XL|L|LX|LXX|LXXX|XC|C|CL|CLIV)$', stripped):
                if stripped not in roman_numeral_markers:
                    roman_numeral_markers.append(stripped)

            # Narrator tags - narrative poems (e.g., "quoth he", "thus she began")
            if re.search(r'\b(quoth|thus\s+(she|he))\b', stripped, re.IGNORECASE):
                has_narrator_tags = True

        return FileTypeFeatures(
            character_names=character_names,
            stage_direction_count=stage_direction_count,
            act_scene_count=act_scene_count,
            quoted_dialogue_count=quoted_dialogue_count,
            roman_numeral_markers=roman_numeral_markers,
            has_narrator_tags=has_narrator_tags
        )

    def detect_file_type(self, features: FileTypeFeatures) -> Tuple[str, float]:
        """
        Detect Shakespeare file type based on extracted features.

        Uses structural features to classify files as plays, sonnets, narrative
        poems, or lyric poems. Returns both the detected type and a confidence
        score.

        Args:
            features: FileTypeFeatures object from extract_features()

        Returns:
            Tuple of (file_type, confidence) where:
                file_type: 'play', 'sonnet', 'narrative_poem', 'lyric_poem', or 'unknown'
                confidence: float 0.0-1.0 indicating detection certainty
        """
        # Calculate feature presence
        has_characters = len(features.character_names) > 0
        has_stage_dirs = features.stage_direction_count > 0
        has_acts_scenes = features.act_scene_count > 0
        has_roman_numerals = len(features.roman_numeral_markers) > 5
        has_many_roman = len(features.roman_numeral_markers) > 20
        has_quoted_dialogue = features.quoted_dialogue_count > 10

        # Play detection - highest priority
        # Plays have character names AND stage directions
        if has_characters and has_stage_dirs:
            # Higher confidence if we also have ACT/SCENE markers
            if has_acts_scenes:
                confidence = 0.95
            else:
                confidence = 0.85
            return ('play', confidence)

        # Sonnet detection
        # Sonnets have many Roman numerals but NO character names
        if has_roman_numerals and not has_characters:
            # Higher confidence if we have many sonnets (154 total in Shakespeare's collection)
            if has_many_roman:
                confidence = 0.95
            else:
                confidence = 0.80
            return ('sonnet', confidence)

        # Narrative poem detection
        # Narrative poems have quoted dialogue AND narrator tags
        if has_quoted_dialogue and features.has_narrator_tags:
            return ('narrative_poem', 0.80)

        # Lyric poem detection (catch-all for poetry)
        # Lyric poems have NO character names and NO stage directions
        if not has_characters and not has_stage_dirs:
            # Lower confidence because this is a catch-all
            return ('lyric_poem', 0.60)

        # Unknown - couldn't classify
        return ('unknown', 0.0)

    def process_line(self, line: str) -> str:
        """Process a single line based on current state."""
        self.lines_processed += 1

        # Stage directions: never modify, but stay in current dialogue state
        # Stage directions can appear within a character's speech
        if self.is_stage_direction(line):
            self.non_dialogue_lines_skipped += 1
            return line

        # Metadata/headers: check BEFORE character names to avoid false matches
        # (e.g., "THESEUS, Duke of Athens" in cast lists)
        if self.is_metadata_or_header(line):
            self.in_dialogue = False
            self.non_dialogue_lines_skipped += 1
            return line

        # Check for inline dialogue (character name + dialogue on same line)
        has_inline, char_name, dialogue = self.has_inline_dialogue(line)
        if has_inline:
            self.in_dialogue = True
            self.dialogue_lines_processed += 1
            # Process just the dialogue part
            modified_dialogue, was_modified = self.strip_punctuation(dialogue)
            if was_modified:
                self.lines_modified += 1
                # Reconstruct line with character name + processed dialogue
                # Preserve original line ending (newline)
                line_ending = line[len(line.rstrip()):]
                reconstructed = f"{char_name} {modified_dialogue}{line_ending}"
                if self.dry_run and len(self.preview_changes) < 50:
                    self.preview_changes.append((self.lines_processed, line.strip(), reconstructed.strip()))
                return reconstructed
            else:
                return line

        # Character names: mark start of dialogue
        if self.is_character_name(line):
            self.in_dialogue = True
            self.non_dialogue_lines_skipped += 1  # Character names are not dialogue
            return line

        # Blank lines: don't change dialogue state
        # Blank lines can appear within speeches (after stage directions) or between speakers
        # Let character names and metadata/headers handle state transitions
        if self.is_blank_or_whitespace(line):
            return line  # Don't count blank lines

        # If we're in dialogue mode, strip punctuation
        if self.in_dialogue:
            self.dialogue_lines_processed += 1
            modified, was_modified = self.strip_punctuation(line)
            if was_modified:
                self.lines_modified += 1
                # Track changes for dry-run preview (limit to first 50)
                if self.dry_run and len(self.preview_changes) < 50:
                    self.preview_changes.append((self.lines_processed, line.strip(), modified.strip()))
            return modified

        # Otherwise, leave line unchanged (non-dialogue content)
        self.non_dialogue_lines_skipped += 1
        return line

    def process_file(self, create_backup: bool = True) -> bool:
        """
        Process the file, stripping punctuation from dialogue lines.
        Returns True if successful.
        """
        if not self.filepath.exists():
            if not self.quiet:
                print(f"Error: File not found: {self.filepath}")
            return False

        # Store original permissions
        original_mode = None
        was_readonly = False

        # Read original content
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            if not self.quiet:
                print(f"Error reading {self.filepath}: {e}")
            return False

        # Detect file type
        content = ''.join(lines)
        features = self.extract_features(content)
        self.file_type, self.confidence = self.detect_file_type(features)

        if not self.quiet:
            print(f"File type detected: {self.file_type} (confidence: {self.confidence:.2f})")
            if self.confidence < 0.8:
                print(f"Warning: Low confidence in file type detection")

        # Poetry protection - block sonnets and lyric poems by default
        if self.file_type in ['sonnet', 'lyric_poem'] and not self.force:
            if not self.quiet:
                print(f"\nError: File detected as '{self.file_type}' (pure poetry).")
                print("This file contains Shakespeare's authorial poetry, not character dialogue.")
                print("Processing would strip punctuation from the author's work.")
                print("Use --force to override (not recommended).")
            return False

        # Narrative poem warning
        if self.file_type == 'narrative_poem' and not self.quiet:
            print("\nWarning: Narrative poem detected.")
            print("This file contains quoted dialogue embedded in verse.")
            print("Processing will only affect dialogue lines, but may impact poetic meter.")
            if not self.force:
                print("Proceeding with caution...")

        # Check if file is read-only
        original_mode = os.stat(self.filepath).st_mode
        if not (original_mode & stat.S_IWUSR):
            was_readonly = True
            # Make file writable temporarily
            try:
                os.chmod(self.filepath, original_mode | stat.S_IWUSR)
            except Exception as e:
                if not self.quiet:
                    print(f"Error: Cannot make file writable: {e}")
                return False

        # Create backup (skip in dry-run mode)
        if create_backup and not self.dry_run:
            backup_path = self.filepath.with_suffix('.txt.bak')

            # If backup already exists, rename it to .bak.1 (keep one previous backup)
            if backup_path.exists():
                old_backup_path = self.filepath.with_suffix('.txt.bak.1')
                try:
                    if old_backup_path.exists():
                        old_backup_path.unlink()  # Remove old .bak.1
                    backup_path.rename(old_backup_path)
                    if not self.quiet and self.verbose:
                        print(f"Renamed existing backup: {backup_path} → {old_backup_path}")
                except Exception as e:
                    if not self.quiet:
                        print(f"Warning: Could not rename existing backup: {e}")

            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                # Make backup read-only if original was read-only
                if was_readonly:
                    os.chmod(backup_path, original_mode)
                if not self.quiet and not self.dry_run:
                    print(f"Backup created: {backup_path}")
            except Exception as e:
                if not self.quiet:
                    print(f"Error: Could not create backup: {e}")
                # Restore permissions and abort if backup creation fails
                if was_readonly and original_mode:
                    try:
                        os.chmod(self.filepath, original_mode)
                    except:
                        pass
                return False

        # Process lines
        processed_lines = []
        for line in lines:
            processed_line = self.process_line(line)
            processed_lines.append(processed_line)

        # Determine output path
        # If source is in unclean-gutenberg, write to gutenberg with -unclean suffix removed
        output_path = self.filepath
        if 'unclean-gutenberg' in str(self.filepath):
            # Create output directory path
            output_dir = Path.home() / "utono" / "literature" / "shakespeare-william" / "gutenberg"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Remove -unclean suffix from filename
            filename = self.filepath.name
            if filename.endswith('-unclean.txt'):
                output_filename = filename.replace('-unclean.txt', '.txt')
            else:
                output_filename = filename

            output_path = output_dir / output_filename

            if not self.quiet and not self.dry_run:
                print(f"Output: {output_path}")

        # Write modified content (skip in dry-run mode)
        if not self.dry_run:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.writelines(processed_lines)
            except Exception as e:
                if not self.quiet:
                    print(f"Error writing {output_path}: {e}")
                return False

        # Report results
        if not self.quiet:
            if self.dry_run:
                self._show_dry_run_preview()
            else:
                print(f"Processed: {self.filepath.name}")
                print(f"  Total lines: {self.lines_processed}")
                print(f"  Lines modified: {self.lines_modified}")
                print(f"  Lines unchanged: {self.lines_processed - self.lines_modified}")
                if self.verbose:
                    self._show_punctuation_stats()
                if was_readonly:
                    print(f"  Permissions: Restored to read-only")

        return True

    def _show_dry_run_preview(self):
        """Show preview of changes for dry-run mode."""
        print(f"\n{'=' * 60}")
        print(f"DRY-RUN PREVIEW: {self.filepath.name}")
        print(f"{'=' * 60}")
        print(f"\nFile type: {self.file_type} (confidence: {self.confidence:.2f})")
        print(f"Total changes: {self.lines_modified} lines would be modified")
        print(f"Total lines: {self.lines_processed}")
        print(f"Dialogue lines: {self.dialogue_lines_processed}")
        print()

        # Show punctuation statistics
        self._show_punctuation_stats()
        print()

        # Show sample changes
        if self.preview_changes:
            print(f"Sample changes (showing first {min(len(self.preview_changes), 20)}):")
            print(f"{'─' * 60}")
            for i, (line_num, original, modified) in enumerate(self.preview_changes[:20], 1):
                print(f"\nLine {line_num}:")
                print(f"  - {original}")
                print(f"  + {modified}")

            if len(self.preview_changes) > 20:
                print(f"\n... and {len(self.preview_changes) - 20} more changes")
        else:
            print("No changes would be made (file already clean)")

        print(f"\n{'─' * 60}")
        print("⚠️  No files were modified (dry-run mode)")
        print("Run without --dry-run to apply changes")
        print(f"{'=' * 60}\n")

    def _show_punctuation_stats(self):
        """Show punctuation removal statistics."""
        total = sum(self.punctuation_removed.values())
        print(f"\nPunctuation to be removed: {total} characters")
        if total > 0:
            print(f"  Commas: {self.punctuation_removed['commas']}")
            print(f"  Semicolons: {self.punctuation_removed['semicolons']}")
            print(f"  Colons: {self.punctuation_removed['colons']}")
            print(f"  Quotes: {self.punctuation_removed['quotes']}")
            print(f"  Dashes: {self.punctuation_removed['dashes']}")


def validate_file(filepath: str) -> ValidationResult:
    """Validate a Shakespeare text file without modifying it.

    Analyzes file structure, detects type, and provides recommendations.
    This is critical for agent workflows to check files before processing.

    Args:
        filepath: Path to the file to validate

    Returns:
        ValidationResult with file type, processability, and recommendations

    Example:
        >>> result = validate_file('hamlet_gut.txt')
        >>> print(f"Type: {result.detected_type}, Safe: {result.is_processable}")
        Type: play, Safe: True
    """
    filepath_obj = Path(filepath)

    # Read file content
    try:
        with open(filepath_obj, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return ValidationResult(
            filepath=str(filepath),
            is_shakespeare_file=False,
            detected_type='unknown',
            confidence=0.0,
            is_processable=False,
            processing_mode='none',
            features=FileTypeFeatures([], 0, 0, 0, [], False),
            warnings=['File not found'],
            recommendation='Cannot validate - file does not exist'
        )
    except PermissionError:
        return ValidationResult(
            filepath=str(filepath),
            is_shakespeare_file=False,
            detected_type='unknown',
            confidence=0.0,
            is_processable=False,
            processing_mode='none',
            features=FileTypeFeatures([], 0, 0, 0, [], False),
            warnings=['Permission denied'],
            recommendation='Cannot validate - insufficient permissions'
        )

    # Create temporary processor to use its methods
    processor = DialogueProcessor(filepath, quiet=True)

    # Extract features and detect file type
    features = processor.extract_features(content)
    file_type, confidence = processor.detect_file_type(features)

    # Check if this appears to be a Shakespeare file
    is_shakespeare = False
    content_lower = content.lower()
    if 'william shakespeare' in content_lower or 'project gutenberg' in content_lower:
        is_shakespeare = True
    elif len(features.character_names) > 5 or features.act_scene_count > 0:
        # Has strong play features even without explicit attribution
        is_shakespeare = True

    # Determine processability and mode
    warnings = []

    if file_type == 'play':
        is_processable = True
        processing_mode = 'dialogue'
        recommendation = 'Safe to process as play - dialogue mode recommended'
        if confidence < 0.8:
            warnings.append(f'Lower confidence ({confidence:.2f}) - verify before processing')

    elif file_type == 'narrative_poem':
        is_processable = True
        processing_mode = 'quoted'
        recommendation = 'Processable with caution - quoted dialogue only (narrative poem)'
        warnings.append('Narrative poem detected - only quoted dialogue will be processed')
        warnings.append('Verify that quoted dialogue is not part of authorial verse')

    elif file_type == 'sonnet':
        is_processable = False
        processing_mode = 'none'
        recommendation = 'Not recommended - pure poetry (sonnet collection)'
        warnings.append('Pure poetry detected - processing would damage authorial work')
        warnings.append('Use --force to override (not recommended)')

    elif file_type == 'lyric_poem':
        is_processable = False
        processing_mode = 'none'
        recommendation = 'Not recommended - pure poetry (lyric poem)'
        warnings.append('Pure poetry detected - processing would damage authorial work')
        warnings.append('Use --force to override (not recommended)')

    else:  # unknown
        is_processable = False
        processing_mode = 'none'
        recommendation = 'Cannot determine file type - specify with --file-type if needed'
        warnings.append('File type detection uncertain')
        if not is_shakespeare:
            warnings.append('File does not appear to be Shakespeare text')

    # Add warning if file doesn't appear to be Shakespeare
    if not is_shakespeare and file_type != 'unknown':
        warnings.append('File may not be Shakespeare text - verify source')

    return ValidationResult(
        filepath=str(filepath),
        is_shakespeare_file=is_shakespeare,
        detected_type=file_type,
        confidence=confidence,
        is_processable=is_processable,
        processing_mode=processing_mode,
        features=features,
        warnings=warnings,
        recommendation=recommendation
    )


def format_validation_result(result: ValidationResult) -> str:
    """Format a ValidationResult for human-readable output.

    Args:
        result: ValidationResult to format

    Returns:
        Formatted string with file type, features, warnings, and recommendation
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"File: {Path(result.filepath).name}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"File Type: {result.detected_type}")
    lines.append(f"Confidence: {result.confidence:.2f}")
    lines.append(f"Shakespeare File: {'Yes' if result.is_shakespeare_file else 'No'}")
    lines.append(f"Processable: {'Yes' if result.is_processable else 'No'}")
    lines.append(f"Processing Mode: {result.processing_mode}")
    lines.append("")

    lines.append("Features Detected:")
    lines.append(f"  Character names: {len(result.features.character_names)}")
    if result.features.character_names:
        sample = result.features.character_names[:5]
        lines.append(f"    Sample: {', '.join(sample)}")
    lines.append(f"  Stage directions: {result.features.stage_direction_count}")
    lines.append(f"  ACT/SCENE markers: {result.features.act_scene_count}")
    lines.append(f"  Quoted dialogue: {result.features.quoted_dialogue_count}")
    lines.append(f"  Roman numerals: {len(result.features.roman_numeral_markers)}")
    if result.features.roman_numeral_markers:
        sample = result.features.roman_numeral_markers[:5]
        lines.append(f"    Sample: {', '.join(sample)}")
    lines.append(f"  Narrator tags: {'Yes' if result.features.has_narrator_tags else 'No'}")
    lines.append("")

    if result.warnings:
        lines.append("Warnings:")
        for warning in result.warnings:
            lines.append(f"  ⚠ {warning}")
        lines.append("")

    lines.append("Recommendation:")
    lines.append(f"  {result.recommendation}")
    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


def select_files_with_fzf(search_dir: str = None) -> List[str]:
    """Use fzf to interactively select files."""
    if search_dir is None:
        search_dir = os.getcwd()

    search_path = Path(search_dir)

    # Find all .txt files
    txt_files = list(search_path.glob('*.txt'))

    if not txt_files:
        print(f"No .txt files found in {search_path}")
        return []

    # Prepare file list for fzf
    file_list = '\n'.join([f.name for f in txt_files])

    try:
        # Run fzf with multi-select enabled
        result = subprocess.run(
            ['fzf', '--multi', '--prompt=Select Shakespeare files to process: '],
            input=file_list,
            text=True,
            capture_output=True,
            check=True
        )

        # Get selected files
        selected_names = result.stdout.strip().split('\n')
        selected_paths = [str(search_path / name) for name in selected_names if name]

        return selected_paths

    except subprocess.CalledProcessError:
        print("File selection cancelled.")
        return []
    except FileNotFoundError:
        print("Error: fzf not found. Please install fzf or provide file arguments.")
        return []


def main():
    """Main entry point."""
    # Default directory for Shakespeare texts
    default_dir = Path.home() / "utono" / "literature" / "shakespeare-william" / "unclean-gutenberg"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="bardclean - Strip punctuation from Shakespeare dialogue lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive selection from default directory
  bardclean

  # Validate files before processing
  bardclean --validate hamlet_gut.txt

  # Preview changes without modifying files
  bardclean --dry-run hamlet_gut.txt

  # Process specific files
  bardclean hamlet_gut.txt macbeth_gut.txt

  # JSON output for agents/scripts
  bardclean --json --validate hamlet_gut.txt

  # Interactive selection from custom directory
  bardclean --dir /path/to/texts

Exit Codes:
  0 = Success
  2 = File not found
  3 = Permission error
  4 = Invalid format (poetry file blocked)
  5 = Validation failed
  6 = No files selected
  7 = User cancelled selection

Default text directory: {default_dir}
        """.format(default_dir=default_dir)
    )

    parser.add_argument(
        'files',
        nargs='*',
        help='Text files to process (if not specified, uses fzf for interactive selection)'
    )

    parser.add_argument(
        '--dir',
        type=str,
        default=str(default_dir),
        help=f'Directory containing text files (default: {default_dir})'
    )

    # Mode flags (mutually exclusive with processing)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--validate',
        action='store_true',
        help='Validate file type and structure without processing'
    )
    mode_group.add_argument(
        '--stats-only',
        action='store_true',
        help='Analyze files and show statistics without processing'
    )
    mode_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    # Safety flags
    parser.add_argument(
        '--force',
        action='store_true',
        help='⚠️  Force processing of poetry files (NOT recommended - will damage sonnets/lyric poems)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='(Deprecated) Backups are not created by default - originals are in unclean-gutenberg/'
    )

    # Output control flags (mutually exclusive)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Detailed output with extra information'
    )
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimal output (errors only)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON (for programmatic/agent use)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='bardclean 1.0.0'
    )

    args = parser.parse_args()

    # Print header (suppress if JSON mode)
    if not args.json:
        print("bardclean - Shakespeare Dialogue Punctuation Processor")
        print("=" * 60)

    # Resolve text directory
    text_dir = Path(args.dir).expanduser().resolve()

    if not text_dir.exists():
        if not args.json:
            print(f"Error: Directory not found: {text_dir}")
        return ExitCode.FILE_NOT_FOUND

    # Determine which files to process
    if args.files:
        # Use command line arguments
        # If files are relative paths, resolve them relative to text_dir
        file_paths = []
        for file in args.files:
            file_path = Path(file)
            if not file_path.is_absolute():
                # Try relative to text_dir first
                candidate = text_dir / file
                if candidate.exists():
                    file_paths.append(str(candidate))
                else:
                    # Fall back to current directory
                    file_paths.append(file)
            else:
                file_paths.append(file)

        if not args.json:
            print(f"Text directory: {text_dir}")
            print(f"Processing {len(file_paths)} file(s) from command line arguments...")
    else:
        # Use fzf for interactive selection
        if not args.json:
            print(f"No files specified. Using fzf to select files from {text_dir}...")
        file_paths = select_files_with_fzf(str(text_dir))

        if not file_paths:
            if not args.json:
                print("No files selected. Exiting.")
            return ExitCode.USER_CANCELLED

    if not args.json:
        print()

    # Validation mode - check files without processing
    if args.validate:
        validation_results = []

        for filepath in file_paths:
            validation_result = validate_file(filepath)
            validation_results.append(validation_result)

            if not args.json:
                print(format_validation_result(validation_result))
                print()

        # Output results
        if args.json:
            # JSON output for validation
            json_output = {
                'mode': 'validation',
                'timestamp': datetime.now().isoformat(),
                'files_validated': len(validation_results),
                'results': [r.to_dict() for r in validation_results]
            }
            print(json.dumps(json_output, indent=2))

        # Determine exit code
        has_errors = any(not r.is_processable for r in validation_results)
        return ExitCode.VALIDATION_FAILED if has_errors else ExitCode.SUCCESS

    # Process each file
    success_count = 0
    fail_count = 0
    poetry_blocked_count = 0
    processing_results = []

    for filepath in file_paths:
        if not args.json and not args.quiet:
            print(f"\n{'─' * 60}")

        # Determine quiet mode
        quiet_mode = args.json or args.quiet

        processor = DialogueProcessor(
            filepath,
            force=args.force,
            quiet=quiet_mode,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Read file for type detection
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            content = ''.join(lines)
            features = processor.extract_features(content)
            file_type, confidence = processor.detect_file_type(features)
            processor.file_type = file_type
            processor.confidence = confidence
        except Exception as e:
            # Create error result
            result_obj = ProcessingResult(
                filepath=str(filepath),
                status='error',
                error_message=f"Error reading file: {e}"
            )
            processing_results.append(result_obj)
            fail_count += 1
            continue

        # Check for poetry blocking
        if file_type in ['sonnet', 'lyric_poem'] and not args.force:
            result_obj = ProcessingResult(
                filepath=str(filepath),
                status='skipped',
                file_type=file_type,
                confidence=confidence,
                error_message=f"Blocked: {file_type} (pure poetry). Use --force to override."
            )
            processing_results.append(result_obj)
            poetry_blocked_count += 1
            fail_count += 1

            if not args.json and not args.quiet:
                print(f"File type detected: {file_type} (confidence: {confidence:.2f})")
                print(f"\nError: File detected as '{file_type}' (pure poetry).")
                print("This file contains Shakespeare's authorial poetry, not character dialogue.")
                print("Use --force to override (not recommended).")
            continue

        # Process the file
        # No backup needed - originals are in unclean-gutenberg directory
        create_backup = False
        success = processor.process_file(create_backup=create_backup)

        # Create result object
        result_obj = ProcessingResult(
            filepath=str(filepath),
            status='success' if success else 'error',
            file_type=file_type,
            confidence=confidence,
            total_lines=processor.lines_processed,
            modified_lines=processor.lines_modified,
            unchanged_lines=processor.lines_processed - processor.lines_modified
        )
        processing_results.append(result_obj)

        if success:
            success_count += 1
        else:
            fail_count += 1

    # Determine exit code
    if fail_count == 0:
        exit_code = ExitCode.SUCCESS
        batch_status = 'success'
    elif poetry_blocked_count > 0 and poetry_blocked_count == fail_count:
        exit_code = ExitCode.INVALID_FORMAT
        batch_status = 'error'
    else:
        exit_code = ExitCode.GENERAL_ERROR
        batch_status = 'partial' if success_count > 0 else 'error'

    # Output results
    if args.json:
        # JSON output
        batch_result = BatchResult(
            status=batch_status,
            exit_code=exit_code,
            timestamp=datetime.now().isoformat(),
            files_processed=success_count,
            files_failed=fail_count,
            files_skipped=poetry_blocked_count,
            results=processing_results
        )
        print(batch_result.to_json())
    else:
        # Human-readable summary
        print(f"\n{'=' * 60}")
        print(f"Summary:")
        print(f"  Successfully processed: {success_count}")
        print(f"  Failed: {fail_count}")
        if poetry_blocked_count > 0:
            print(f"  Blocked (poetry): {poetry_blocked_count}")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
