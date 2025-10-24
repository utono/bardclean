#!/usr/bin/env python3
"""
Comprehensive test of all implemented features:
- Phase 1.3: Poetry Protection
- Phase 2.4: Exit Codes
- Phase 3.1: JSON Output
"""

import subprocess
import json
import sys
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

def test_poetry_blocking():
    """Test that poetry files are blocked by default."""
    print("\n" + "="*60)
    print("TEST 1: Poetry Protection (Phase 1.3)")
    print("="*60)

    base_dir = Path.home() / "utono/literature/shakespeare-william/gutenberg"
    sonnet_file = base_dir / "sonnets_gut.txt"

    if not sonnet_file.exists():
        print("⚠ Skipping: sonnets_gut.txt not found")
        return

    # Test 1a: Should block without --force
    print("\n1a. Testing poetry blocking (without --force)...")
    result = run_bardclean(str(sonnet_file))

    if result.returncode == 4:  # ExitCode.INVALID_FORMAT
        print("✓ PASS: Poetry file blocked with exit code 4 (INVALID_FORMAT)")
    else:
        print(f"✗ FAIL: Expected exit code 4, got {result.returncode}")

    if "pure poetry" in result.stdout:
        print("✓ PASS: Error message explains poetry blocking")
    else:
        print("✗ FAIL: Error message missing")

    # Test 1b: Should process with --force
    print("\n1b. Testing --force override...")
    result = run_bardclean('--force', str(sonnet_file))

    # Note: This might fail for other reasons, but shouldn't be blocked
    if "pure poetry" in result.stdout and "Use --force" in result.stdout:
        print("✗ FAIL: Still showing block message with --force")
    else:
        print("✓ PASS: --force override working (no block message)")

def test_exit_codes():
    """Test that exit codes are set correctly."""
    print("\n" + "="*60)
    print("TEST 2: Exit Codes (Phase 2.4)")
    print("="*60)

    base_dir = Path.home() / "utono/literature/shakespeare-william/gutenberg"
    hamlet_file = base_dir / "hamlet_gut.txt"
    sonnet_file = base_dir / "sonnets_gut.txt"

    # Test 2a: Success code for valid play
    if hamlet_file.exists():
        print("\n2a. Testing SUCCESS (0) for valid play...")
        result = run_bardclean(str(hamlet_file))

        if result.returncode == 0:
            print(f"✓ PASS: Exit code 0 (SUCCESS) for valid play")
        else:
            print(f"✗ FAIL: Expected 0, got {result.returncode}")
    else:
        print("⚠ Skipping: hamlet_gut.txt not found")

    # Test 2b: Invalid format code for poetry
    if sonnet_file.exists():
        print("\n2b. Testing INVALID_FORMAT (4) for poetry...")
        result = run_bardclean(str(sonnet_file))

        if result.returncode == 4:
            print(f"✓ PASS: Exit code 4 (INVALID_FORMAT) for poetry")
        else:
            print(f"✗ FAIL: Expected 4, got {result.returncode}")
    else:
        print("⚠ Skipping: sonnets_gut.txt not found")

    # Test 2c: User cancelled
    print("\n2c. Testing USER_CANCELLED (7) for no selection...")
    # Note: Can't easily test fzf cancellation automatically
    print("⊘ SKIP: Interactive test (would require fzf interaction)")

def test_json_output():
    """Test JSON output mode."""
    print("\n" + "="*60)
    print("TEST 3: JSON Output (Phase 3.1)")
    print("="*60)

    base_dir = Path.home() / "utono/literature/shakespeare-william/gutenberg"
    hamlet_file = base_dir / "hamlet_gut.txt"
    sonnet_file = base_dir / "sonnets_gut.txt"

    # Test 3a: JSON structure for success
    if hamlet_file.exists():
        print("\n3a. Testing JSON output for successful processing...")
        result = run_bardclean('--json', str(hamlet_file))

        try:
            data = json.loads(result.stdout)
            print("✓ PASS: Valid JSON output")

            # Check required fields
            required_fields = ['status', 'exit_code', 'timestamp', 'files_processed', 'results']
            missing = [f for f in required_fields if f not in data]

            if not missing:
                print(f"✓ PASS: All required fields present: {required_fields}")
            else:
                print(f"✗ FAIL: Missing fields: {missing}")

            # Check result structure
            if data.get('results') and len(data['results']) > 0:
                print("✓ PASS: Results array populated")

                result_obj = data['results'][0]
                result_fields = ['filepath', 'status', 'file_type', 'confidence']
                missing_result = [f for f in result_fields if f not in result_obj]

                if not missing_result:
                    print(f"✓ PASS: Result object has required fields")
                else:
                    print(f"✗ FAIL: Result missing fields: {missing_result}")

                # Display sample
                print("\nSample JSON structure:")
                print(json.dumps(data, indent=2)[:500] + "...")

            else:
                print("✗ FAIL: Results array empty or missing")

        except json.JSONDecodeError as e:
            print(f"✗ FAIL: Invalid JSON: {e}")
            print(f"Output: {result.stdout[:200]}")
    else:
        print("⚠ Skipping: hamlet_gut.txt not found")

    # Test 3b: JSON for poetry blocking
    if sonnet_file.exists():
        print("\n3b. Testing JSON output for blocked poetry...")
        result = run_bardclean('--json', str(sonnet_file))

        try:
            data = json.loads(result.stdout)
            print("✓ PASS: Valid JSON for blocked file")

            if data.get('exit_code') == 4:
                print("✓ PASS: Exit code 4 in JSON output")
            else:
                print(f"✗ FAIL: Expected exit_code 4, got {data.get('exit_code')}")

            if data.get('files_skipped', 0) > 0:
                print("✓ PASS: files_skipped count present")
            else:
                print("✗ FAIL: files_skipped not tracked")

            # Check result status
            if data.get('results') and data['results'][0].get('status') == 'skipped':
                print("✓ PASS: Result status is 'skipped'")
            else:
                print("✗ FAIL: Result status not 'skipped'")

        except json.JSONDecodeError as e:
            print(f"✗ FAIL: Invalid JSON: {e}")
    else:
        print("⚠ Skipping: sonnets_gut.txt not found")

def main():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# COMPREHENSIVE FEATURE TEST")
    print("# Testing Phases 1.3, 2.4, and 3.1")
    print("#"*60)

    test_poetry_blocking()
    test_exit_codes()
    test_json_output()

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
