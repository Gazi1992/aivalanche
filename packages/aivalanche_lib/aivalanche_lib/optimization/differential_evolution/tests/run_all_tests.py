"""
Run all Differential Evolution tests.

This script runs all individual test modules in sequence.
Each test saves its results in a timestamped subdirectory under results/.
"""

import os
import sys
import subprocess
from datetime import datetime

def run_test(test_name: str, script_name: str):
    """Run a single test script."""
    print(f"\n{'='*60}")
    print(f"Running {test_name}")
    print(f"{'='*60}")
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[PASS] {test_name} completed successfully")
            # Print last few lines of output (summary)
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) > 5:
                print("\nTest output (last 5 lines):")
                for line in output_lines[-5:]:
                    print(f"  {line}")
        else:
            print(f"[FAIL] {test_name} failed with return code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            
    except Exception as e:
        print(f"[FAIL] {test_name} failed with exception: {e}")


def main():
    """Run all tests in sequence."""
    print("Differential Evolution Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Change to test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    # Define tests to run
    tests = [
        ("Adaptive Boundaries Test", "test_adaptive_boundaries.py"),
        ("Initial Population Test", "test_initial_population.py"),
        ("DE Performance Test", "test_de_performance.py"),
        # Add more tests as they are created:
        # ("Operators Test", "test_operators.py"),
        # ("Perturbation Test", "test_perturbation.py"),
        # ("Refinement Test", "test_refinement.py"),
        # ("DE Comparison Test", "test_de_comparison.py"),
    ]
    
    # Run each test
    for test_name, script_name in tests:
        if os.path.exists(script_name):
            run_test(test_name, script_name)
        else:
            print(f"\n[SKIP] Skipping {test_name} - {script_name} not found")
    
    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nResults are saved in: {os.path.join(test_dir, 'results')}")


if __name__ == "__main__":
    main()