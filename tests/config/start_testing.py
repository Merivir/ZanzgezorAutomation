import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.config.automation_config import get_module_active_sections, get_modules_active, load_config


def selected_test_paths(config):
    paths = []
    for module_name in get_modules_active(config):
        module_dir = Path("tests/modules") / module_name
        sections = get_module_active_sections(config, module_name)

        if sections:
            paths.extend(module_dir / f"test_{section}.py" for section in sections)
        else:
            module_test = module_dir / f"test_{module_name}.py"
            if module_test.is_file():
                paths.append(module_test)

    return [str(path) for path in paths if path.is_file()]


def main():
    paths = selected_test_paths(load_config())
    if not paths:
        raise SystemExit("No enabled test files were found in the configuration.")

    # Preserve the original behavior: run every case belonging to enabled sections.
    command = [sys.executable, "-m", "pytest", "--suite", "all", "-v", "-s", *paths]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
