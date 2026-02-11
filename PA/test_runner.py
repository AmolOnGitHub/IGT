#!/usr/bin/env python3
"""
Test Runner for Nash Equilibrium Solver
========================================

Usage:
    python test_runner.py <solution_file.py> <tests_directory>

Example:
    python test_runner.py PA1/soln_q2.py PA1/tests/
"""

import sys
import os
import subprocess
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


def run_test(solution_file, input_file, output_file, timeout=60):
    """Run a single test case and compare outputs."""
    try:
        with open(input_file, 'r') as f:
            input_data = f.read()
        
        with open(output_file, 'r') as f:
            expected_output = f.read().strip()
        
        # Run the solution
        result = subprocess.run(
            ['python3', solution_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return False, f"Runtime error: {result.stderr}", ""
        
        actual_output = result.stdout.strip()
        
        # Direct string comparison
        if actual_output == expected_output:
            return True, "Output matches", actual_output
        else:
            return False, "Output mismatch", actual_output
        
    except subprocess.TimeoutExpired:
        return False, f"Timeout (>{timeout}s)", ""
    except FileNotFoundError as e:
        return False, f"File not found: {e}", ""
    except Exception as e:
        return False, f"Error: {e}", ""


def main():
    if len(sys.argv) != 3:
        print("Usage: python test_runner.py <solution_file.py> <tests_directory>")
        print("Example: python test_runner.py PA1/soln_q2.py PA1/tests/")
        sys.exit(1)
    
    solution_file = sys.argv[1]
    tests_dir = Path(sys.argv[2])
    
    if not os.path.isfile(solution_file):
        print(f"Error: Solution file '{solution_file}' not found")
        sys.exit(1)
    
    if not tests_dir.is_dir():
        print(f"Error: Tests directory '{tests_dir}' not found")
        sys.exit(1)
    
    # Find test files
    test_files = []
    for input_file in sorted(tests_dir.glob('*.in')):
        output_file = input_file.with_suffix('.out')
        if output_file.exists():
            test_files.append((input_file.stem, str(input_file), str(output_file)))
    
    if not test_files:
        print(f"No test files found in {tests_dir}")
        sys.exit(1)
    
    print(f"Running {len(test_files)} test(s)")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, input_file, output_file in test_files:
        print(f"{test_name}...", end=" ")
        is_pass, message, actual_output = run_test(solution_file, input_file, output_file)
        
        if is_pass:
            print(f"{GREEN}PASS{RESET}")
            passed += 1
        else:
            print(f"{RED}FAIL{RESET} - {message}")
            failed += 1
    
    print("=" * 70)
    if failed == 0:
        print(f"{GREEN}Results: {passed} passed, {failed} failed{RESET}")
    else:
        print(f"Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
