#!/usr/bin/env python3
"""
Quick test of file type detection feature.
Tests with different Shakespeare file types.
"""

import sys
from pathlib import Path

# Add parent directory to path to import bardclean
sys.path.insert(0, str(Path(__file__).parent))

from bardclean import DialogueProcessor

def test_file(filepath):
    """Test file type detection on a single file."""
    print(f"\n{'='*60}")
    print(f"Testing: {Path(filepath).name}")
    print(f"{'='*60}")

    processor = DialogueProcessor(filepath)

    # Read file and detect type
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract features
        features = processor.extract_features(content)

        # Detect file type
        file_type, confidence = processor.detect_file_type(features)

        # Display results
        print(f"\nFile Type: {file_type}")
        print(f"Confidence: {confidence:.2f}")
        print(f"\nFeatures Extracted:")
        print(f"  Character names: {len(features.character_names)}")
        if features.character_names:
            print(f"    First 5: {features.character_names[:5]}")
        print(f"  Stage directions: {features.stage_direction_count}")
        print(f"  ACT/SCENE markers: {features.act_scene_count}")
        print(f"  Quoted dialogue: {features.quoted_dialogue_count}")
        print(f"  Roman numerals: {len(features.roman_numeral_markers)}")
        if features.roman_numeral_markers:
            print(f"    Found: {features.roman_numeral_markers[:10]}")
        print(f"  Has narrator tags: {features.has_narrator_tags}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Test file type detection with various Shakespeare files."""

    base_dir = Path.home() / "utono/literature/shakespeare-william/gutenberg"

    test_files = [
        base_dir / "hamlet_gut.txt",           # Should detect: play
        base_dir / "sonnets_gut.txt",          # Should detect: sonnet
        base_dir / "venus_and_adonis_gut.txt", # Should detect: narrative_poem
    ]

    print("\n" + "="*60)
    print("FILE TYPE DETECTION TEST")
    print("="*60)

    for filepath in test_files:
        if filepath.exists():
            test_file(filepath)
        else:
            print(f"\nSkipping (not found): {filepath}")

    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
