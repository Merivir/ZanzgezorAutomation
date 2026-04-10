# Add the project root to Python path so imports work
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import your functions
from tests.config.automation_config import get_modules_active, load_config, get_user_credentials, get_module_active_sections

# Load config
config = load_config()
print("Config loaded!")

# Test different parameters
admin_creds = get_user_credentials(config, "admin")
print("Admin:", admin_creds)

agent_creds = get_user_credentials(config, "agent") 
print("Agent:", agent_creds)

# Test error cases
try:
    invalid_creds = get_user_credentials(config, "nonexistent_role")
except ValueError as e:
    print("Error (expected):", e)


active_modules = get_modules_active(config)

if active_modules:
    print("Modules are active!")
    print("Active Modules:", active_modules)
else:    
    print("No active modules found.")  
    raise ValueError("No active modules found in configuration.")



# i want to take active modules, and activate that run by the exact name of the module, and then run the test cases for that module.
for module_name in active_modules:
    print(f"Running tests for module: {module_name}")

    active_sections = get_module_active_sections(config, module_name)
    print(f"Active sections for module '{module_name}': {active_sections}")
    
    # So i need to call modules/{module_name}/test_{module_name}.py and run the test cases in that file.
    test_file = f"tests/modules/{module_name}/test_{module_name}.py"
    if os.path.exists(test_file):
        print(f"Running tests in {test_file}...")
        os.environ["ACTIVE_SECTIONS"] = ",".join(active_sections)
        os.system(f"python {test_file}")
    else:
        print(f"Test file {test_file} not found. Skipping tests for module: {module_name}")

