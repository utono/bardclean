#!/usr/bin/env python3
"""
Test validation mode implementation (Phase 2.2)
"""

import subprocess
import json
from pathlib import Path


def run_bardclean(*args):
    """Run bardclean with given arguments and return result."""
    cmd = ['python3', 'bardclean.py'] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    return result


def test_validation_mode():
    """Test validation mode functionality."""
    print("\n" + "=" * 60)
    print("TEST: Validation Mode (Phase 2.2)")
    print("=" * 60)

    base_dir = Path.home() / "utono/literature/shakespeare-william/gutenberg"
    hamlet_file = base_dir / "hamlet_gut.txt"
    sonnet_file = base_dir / "sonnets_gut.txt"
    venus_file = base_dir / "venus_and_adonis_gut.txt"

    # Test 1: Validate a play (human-readable output)
    if hamlet_file.exists():
        print("\n1. Testing --validate with play (Hamlet)...")
        result = run_bardclean('--validate', str(hamlet_file))

        if result.returncode == 0:
            print("✓ PASS: Exit code 0 (SUCCESS)")
        else:
            print(f"✗ FAIL: Expected exit code 0, got {result.returncode}")

        if "File Type: play" in result.stdout:
            print("✓ PASS: Detected as play")
        else:
            print("✗ FAIL: Not detected as play")

        if "Processable: Yes" in result.stdout:
            print("✓ PASS: Marked as processable")
        else:
            print("✗ FAIL: Not marked as processable")

        if "Recommendation:" in result.stdout:
            print("✓ PASS: Recommendation included")
        else:
            print("✗ FAIL: Recommendation missing")

        print("\nSample output:")
        print(result.stdout[:500])

    # Test 2: Validate poetry (should fail validation)
    if sonnet_file.exists():
        print("\n2. Testing --validate with poetry (Sonnets)...")
        result = run_bardclean('--validate', str(sonnet_file))

        if result.returncode == 5:  # VALIDATION_FAILED
            print("✓ PASS: Exit code 5 (VALIDATION_FAILED)")
        else:
            print(f"✗ FAIL: Expected exit code 5, got {result.returncode}")

        if "File Type: sonnet" in result.stdout:
            print("✓ PASS: Detected as sonnet")
        else:
            print("✗ FAIL: Not detected as sonnet")

        if "Processable: No" in result.stdout:
            print("✓ PASS: Marked as not processable")
        else:
            print("✗ FAIL: Incorrectly marked as processable")

        if "Warnings:" in result.stdout:
            print("✓ PASS: Warnings included")
        else:
            print("✗ FAIL: Warnings missing")

    # Test 3: Validate with JSON output
    if hamlet_file.exists():
        print("\n3. Testing --validate --json...")
        result = run_bardclean('--validate', '--json', str(hamlet_file))

        try:
            data = json.loads(result.stdout)
            print("✓ PASS: Valid JSON output")

            if data.get('mode') == 'validation':
                print("✓ PASS: Mode is 'validation'")
            else:
                print(f"✗ FAIL: Expected mode='validation', got {data.get('mode')}")

            if 'results' in data and len(data['results']) > 0:
                print("✓ PASS: Results array present")

                r = data['results'][0]
                required_fields = ['filepath', 'detected_type', 'confidence',
                                   'is_processable', 'processing_mode', 'features',
                                   'warnings', 'recommendation']
                missing = [f for f in required_fields if f not in r]

                if not missing:
                    print(f"✓ PASS: All required fields present")
                else:
                    print(f"✗ FAIL: Missing fields: {missing}")

                if r.get('features', {}).get('character_count', 0) > 0:
                    print("✓ PASS: Character count present")
                else:
                    print("✗ FAIL: Character count missing or zero")

            print("\nSample JSON:")
            print(json.dumps(data, indent=2)[:500] + "...")

        except json.JSONDecodeError as e:
            print(f"✗ FAIL: Invalid JSON: {e}")
            print(f"Output: {result.stdout[:200]}")

    # Test 4: Validate narrative poem
    if venus_file.exists():
        print("\n4. Testing --validate with narrative poem...")
        result = run_bardclean('--validate', str(venus_file))

        if "narrative_poem" in result.stdout:
            print("✓ PASS: Detected as narrative_poem")
        else:
            print("✗ FAIL: Not detected as narrative_poem")

        if "Processable: Yes" in result.stdout:
            print("✓ PASS: Marked as processable (with caution)")
        else:
            print("✗ FAIL: Not marked as processable")

        if "Processing Mode: quoted" in result.stdout:
            print("✓ PASS: Processing mode is 'quoted'")
        else:
            print("✗ FAIL: Processing mode not 'quoted'")

    print("\n" + "=" * 60)
    print("VALIDATION MODE TEST COMPLETE")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    test_validation_mode()
