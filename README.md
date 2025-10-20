# bardclean

Strip punctuation from Shakespeare dialogue lines while preserving sentence structure.

## Overview

**bardclean** is a Python tool that intelligently processes Shakespeare play texts from Project Gutenberg, removing specific punctuation marks from character dialogue while preserving essential elements like periods, question marks, and apostrophes.

## Features

- ✅ **Smart Dialogue Detection** - Uses state machine to identify dialogue vs stage directions
- ✅ **Selective Punctuation Removal** - Removes commas, semicolons, colons, exclamation marks, quotes, and dashes
- ✅ **Preserves Essential Punctuation** - Keeps periods (`.`), question marks (`?`), and apostrophes (`'`)
- ✅ **Read-Only File Support** - Handles read-only files with automatic permission management
- ✅ **Backup Creation** - Creates `.bak` backups before processing
- ✅ **Interactive File Selection** - Uses `fzf` for easy multi-file selection
- ✅ **Configurable Directory** - Specify custom text file directory with `--dir` flag

## Installation

```bash
# Clone the repository
git clone https://github.com/utono/bardclean.git
cd bardclean

# Make script executable (if needed)
chmod +x bardclean.py
```

## Requirements

- Python 3.8+
- `fzf` (optional, for interactive file selection)

## Usage

### Basic Usage

```bash
# Interactive selection from default directory
./bardclean.py

# Process specific files
./bardclean.py hamlet_gut.txt macbeth_gut.txt

# Show help
./bardclean.py --help
```

### Custom Directory

```bash
# Interactive selection from custom directory
./bardclean.py --dir /path/to/shakespeare/texts

# Process specific files from custom directory
./bardclean.py --dir /path/to/texts file1.txt file2.txt
```

### Default Directory

By default, bardclean looks for files in:
```
~/utono/literature/shakespeare-william/gutenberg
```

You can override this with the `--dir` flag.

## How It Works

### Dialogue Detection

bardclean uses a state machine to identify dialogue:

1. **Character Name Detection** - Recognizes patterns like `HAMLET.`, `OPHELIA.`, `Ber.`
2. **Dialogue Mode** - Enters dialogue processing after character name
3. **Exit Conditions** - Exits on blank lines, stage directions, or new character

### Punctuation Processing

**Removed:**
- Commas: `,`
- Semicolons: `;`
- Colons: `:`
- Exclamation marks: `!`
- Quotation marks: `"`
- Hyphens/Dashes: `-`, `—`, `–`

**Preserved:**
- Periods: `.`
- Question marks: `?`
- Apostrophes: `'`

### Example

**Before:**
```
HAMLET.
To be, or not to be: that is the question.
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles,
And by opposing end them!
```

**After:**
```
HAMLET.
To be or not to be that is the question.
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune
Or to take arms against a sea of troubles
And by opposing end them
```

## File Structure

```
bardclean/
├── bardclean.py          # Main script
├── PRD.md                # Product Requirements Document
├── planning.md           # Comprehensive planning documentation
└── README.md             # This file
```

## Documentation

- **[PRD.md](PRD.md)** - Detailed product requirements, user stories, and specifications
- **[planning.md](planning.md)** - Complete planning history, algorithm design, and implementation notes

## Supported File Types

bardclean is designed for **Shakespeare plays** from Project Gutenberg:

- ✅ **Plays** (38 files) - Hamlet, Macbeth, Romeo and Juliet, etc.
- ⚠️ **Narrative Poems** (2 files) - Venus and Adonis, Rape of Lucrece
- ❌ **Pure Poetry** (4+ files) - Sonnets, lyric poems (not recommended)

## Future Enhancements

Planned features (see [planning.md](planning.md) for details):

- JSON output for programmatic use
- File type validation mode
- Dry-run preview
- Narrative poem support
- Coding agent integration

## Contributing

This project is in active development. See [PRD.md](PRD.md) and [planning.md](planning.md) for roadmap and implementation details.

## License

This project is open source. See LICENSE file for details.

## Author

Created by utono

## Repository

https://github.com/utono/bardclean
