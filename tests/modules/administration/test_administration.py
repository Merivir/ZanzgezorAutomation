import os

print("Running tests for module: ")
print("Beginning of test_administration.py")

active_sections = os.getenv("ACTIVE_SECTIONS", "").split(",")
print(f"Active sections for this module: {active_sections}")

for section in active_sections:
    print(f"Running tests for section: {section}")
    test_file = f"tests/modules/administration/test_{section}.py"
    if os.path.exists(test_file):
        print(f"Running tests in {test_file}...")
        os.system(f"pytest -s {test_file}")
    else:
        print(f"Test file {test_file} not found. Skipping tests for section: {section}")