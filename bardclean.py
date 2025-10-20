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
from pathlib import Path
from typing import List, Tuple, Optional


class DialogueProcessor:
    """Process Shakespeare text files to strip punctuation from dialogue."""

    # Punctuation to remove (everything except period, apostrophe, and question mark)
    PUNCT_PATTERN = re.compile(r"[,;:!\"\-—–]")

    # Character name pattern: all caps or mixed case, short line, ends with period
    # Matches: TROILUS., Ber., PANDARUS., AJAX., etc.
    CHAR_NAME_PATTERN = re.compile(r'^[A-Z][A-Za-z\s]*\.$')

    # Stage direction pattern: enclosed in brackets
    STAGE_DIR_PATTERN = re.compile(r'^\[.*\]$')

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.in_dialogue = False
        self.lines_processed = 0
        self.lines_modified = 0

    def is_character_name(self, line: str) -> bool:
        """Check if line is a character name."""
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
        if stripped.isupper() and len(stripped) > 1:
            return True

        # Scene/Act markers
        if stripped.startswith(('ACT ', 'SCENE', 'Scene ', 'PROLOGUE', 'EPILOGUE')):
            return True

        # Cast list lines (Name, description)
        if ', ' in stripped and not self.in_dialogue:
            return True

        return False

    def strip_punctuation(self, line: str) -> Tuple[str, bool]:
        """
        Strip punctuation from line, preserving periods.
        Returns (modified_line, was_modified).
        """
        original = line
        modified = self.PUNCT_PATTERN.sub('', line)
        return modified, (original != modified)

    def process_line(self, line: str) -> str:
        """Process a single line based on current state."""
        self.lines_processed += 1

        # Stage directions: never modify
        if self.is_stage_direction(line):
            self.in_dialogue = False
            return line

        # Character names: mark start of dialogue
        if self.is_character_name(line):
            self.in_dialogue = True
            return line

        # Blank lines: end dialogue state
        if self.is_blank_or_whitespace(line):
            self.in_dialogue = False
            return line

        # Metadata/headers: never modify
        if self.is_metadata_or_header(line):
            self.in_dialogue = False
            return line

        # If we're in dialogue mode, strip punctuation
        if self.in_dialogue:
            modified, was_modified = self.strip_punctuation(line)
            if was_modified:
                self.lines_modified += 1
            return modified

        # Otherwise, leave line unchanged
        return line

    def process_file(self, create_backup: bool = True) -> bool:
        """
        Process the file, stripping punctuation from dialogue lines.
        Returns True if successful.
        """
        if not self.filepath.exists():
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
            print(f"Error reading {self.filepath}: {e}")
            return False

        # Check if file is read-only
        original_mode = os.stat(self.filepath).st_mode
        if not (original_mode & stat.S_IWUSR):
            was_readonly = True
            # Make file writable temporarily
            try:
                os.chmod(self.filepath, original_mode | stat.S_IWUSR)
            except Exception as e:
                print(f"Error: Cannot make file writable: {e}")
                return False

        # Create backup
        if create_backup:
            backup_path = self.filepath.with_suffix('.txt.bak')
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                # Make backup read-only if original was read-only
                if was_readonly:
                    os.chmod(backup_path, original_mode)
                print(f"Backup created: {backup_path}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")

        # Process lines
        processed_lines = []
        for line in lines:
            processed_line = self.process_line(line)
            processed_lines.append(processed_line)

        # Write modified content
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.writelines(processed_lines)
        except Exception as e:
            print(f"Error writing {self.filepath}: {e}")
            # Restore original permissions even on error
            if was_readonly and original_mode:
                try:
                    os.chmod(self.filepath, original_mode)
                except:
                    pass
            return False

        # Restore original permissions if file was read-only
        if was_readonly and original_mode:
            try:
                os.chmod(self.filepath, original_mode)
            except Exception as e:
                print(f"Warning: Could not restore original permissions: {e}")

        # Report results
        print(f"Processed: {self.filepath.name}")
        print(f"  Total lines: {self.lines_processed}")
        print(f"  Lines modified: {self.lines_modified}")
        print(f"  Lines unchanged: {self.lines_processed - self.lines_modified}")
        if was_readonly:
            print(f"  Permissions: Restored to read-only")

        return True


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
    default_dir = Path.home() / "utono" / "literature" / "shakespeare-william" / "gutenberg"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="bardclean - Strip punctuation from Shakespeare dialogue lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive selection from default directory
  bardclean

  # Process specific files
  bardclean hamlet_gut.txt macbeth_gut.txt

  # Interactive selection from custom directory
  bardclean --dir /path/to/texts

  # Process files from custom directory
  bardclean --dir /path/to/texts file1.txt file2.txt

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

    args = parser.parse_args()

    # Print header
    print("bardclean - Shakespeare Dialogue Punctuation Processor")
    print("=" * 60)

    # Resolve text directory
    text_dir = Path(args.dir).expanduser().resolve()

    if not text_dir.exists():
        print(f"Error: Directory not found: {text_dir}")
        return 2

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

        print(f"Text directory: {text_dir}")
        print(f"Processing {len(file_paths)} file(s) from command line arguments...")
    else:
        # Use fzf for interactive selection
        print(f"No files specified. Using fzf to select files from {text_dir}...")
        file_paths = select_files_with_fzf(str(text_dir))

        if not file_paths:
            print("No files selected. Exiting.")
            return 1

    print()

    # Process each file
    success_count = 0
    fail_count = 0

    for filepath in file_paths:
        print(f"\n{'─' * 60}")
        processor = DialogueProcessor(filepath)
        if processor.process_file(create_backup=True):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Successfully processed: {success_count}")
    print(f"  Failed: {fail_count}")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
