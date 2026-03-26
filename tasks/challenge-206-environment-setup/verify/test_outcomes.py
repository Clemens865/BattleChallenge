"""Outcome-based tests for challenge-206: Environment Setup & Dependency Resolution."""

import json
import os
import re

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
TASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(TASK_DIR, "input", "project")


def _read_file(relative_path):
    """Read a file from OUTPUT_DIR, return contents or None."""
    path = os.path.join(OUTPUT_DIR, relative_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_input_file(relative_path):
    """Read a file from INPUT_DIR, return contents or None."""
    path = os.path.join(INPUT_DIR, relative_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _load_package_json():
    """Load and parse package.json from OUTPUT_DIR."""
    content = _read_file("package.json")
    if content is None:
        pytest.skip("package.json not found")
    return json.loads(content)


def _load_tsconfig():
    """Load and parse tsconfig.json from OUTPUT_DIR."""
    content = _read_file("tsconfig.json")
    if content is None:
        pytest.skip("tsconfig.json not found")
    # Strip comments (tsconfig allows them)
    stripped = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    return json.loads(stripped)


def _parse_semver_major(version_str):
    """Extract major version from a semver range like ^4.0.0 or ~5.1.0."""
    match = re.search(r"(\d+)\.\d+\.\d+", version_str)
    if match:
        return int(match.group(1))
    return None


# ===========================================================================
# SECTION 1: package.json validity (3 tests)
# ===========================================================================

def test_package_json_valid():
    """package.json must be valid JSON."""
    content = _read_file("package.json")
    assert content is not None, "package.json not found"
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"package.json is not valid JSON: {e}")


def test_package_json_has_name():
    """package.json must have a name field."""
    pkg = _load_package_json()
    assert "name" in pkg, "package.json missing 'name' field"


def test_package_json_has_dependencies():
    """package.json must have dependencies."""
    pkg = _load_package_json()
    assert "dependencies" in pkg, "package.json missing 'dependencies'"


# ===========================================================================
# SECTION 2: Express version fix (3 tests)
# ===========================================================================

def test_express_version_compatible():
    """Express must be version 4.x or higher (code uses Express 4+ API)."""
    pkg = _load_package_json()
    deps = pkg.get("dependencies", {})
    express_version = deps.get("express", "")
    major = _parse_semver_major(express_version)
    assert major is not None, f"Cannot parse Express version: {express_version}"
    assert major >= 4, (
        f"Express version {express_version} is too old, need >= 4.x"
    )


def test_express_not_version_3():
    """Express must NOT be version 3.x."""
    pkg = _load_package_json()
    deps = pkg.get("dependencies", {})
    express_version = deps.get("express", "")
    assert "3.0.0" not in express_version, (
        "Express is still pinned to 3.0.0"
    )


def test_express_types_installed():
    """@types/express should be in devDependencies."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    assert "@types/express" in dev_deps, (
        "@types/express not found in devDependencies"
    )


# ===========================================================================
# SECTION 3: TypeScript version fix (3 tests)
# ===========================================================================

def test_typescript_version_compatible():
    """TypeScript must be version 5.x+ (tsconfig uses TS5 features)."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    ts_version = dev_deps.get("typescript", "")
    major = _parse_semver_major(ts_version)
    assert major is not None, f"Cannot parse TypeScript version: {ts_version}"
    assert major >= 5, (
        f"TypeScript version {ts_version} is too old, need >= 5.x"
    )


def test_typescript_not_version_4():
    """TypeScript must NOT be version 4.x."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    ts_version = dev_deps.get("typescript", "")
    major = _parse_semver_major(ts_version)
    if major is not None:
        assert major != 4, "TypeScript is still version 4.x"


def test_types_node_installed():
    """@types/node should be in devDependencies for Node.js types."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    # This is a common requirement; frameworks should detect the need
    has_types = "@types/node" in dev_deps
    # Allow skip if they solved it another way
    if not has_types:
        pytest.skip("@types/node not required if types resolve otherwise")


# ===========================================================================
# SECTION 4: Module system consistency (3 tests)
# ===========================================================================

def test_tsconfig_valid():
    """tsconfig.json must be valid JSON (with comments stripped)."""
    content = _read_file("tsconfig.json")
    assert content is not None, "tsconfig.json not found"
    stripped = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    try:
        json.loads(stripped)
    except json.JSONDecodeError as e:
        pytest.fail(f"tsconfig.json is not valid JSON: {e}")


def test_module_system_consistent():
    """tsconfig module setting must be consistent with package.json type field.

    The source code uses ESM import/export syntax. The configuration must
    support this — either via tsconfig module set to a Node-compatible ESM
    setting, or by keeping commonjs with esModuleInterop (which is valid
    for TypeScript compilation of import syntax to CJS require calls).
    """
    tsconfig = _load_tsconfig()
    compiler = tsconfig.get("compilerOptions", {})
    module_setting = compiler.get("module", "").lower()
    es_interop = compiler.get("esModuleInterop", False)

    pkg = _load_package_json()
    pkg_type = pkg.get("type", "")

    # Valid combinations:
    # 1. module=commonjs + esModuleInterop=true (TS compiles ESM imports to CJS)
    # 2. module=nodenext/node16/esnext + type=module in package.json
    # 3. module=es2020/es2022/esnext + appropriate bundler setup
    valid = False
    if module_setting == "commonjs" and es_interop:
        valid = True
    elif module_setting in ("nodenext", "node16") and pkg_type == "module":
        valid = True
    elif module_setting in ("nodenext", "node16"):
        # nodenext/node16 can work without type=module
        valid = True
    elif "es" in module_setting and module_setting != "commonjs":
        valid = True

    assert valid, (
        f"Module system inconsistent: tsconfig module={module_setting}, "
        f"esModuleInterop={es_interop}, package.json type={pkg_type}"
    )


def test_esmodule_interop_enabled():
    """esModuleInterop should be true for default import compatibility."""
    tsconfig = _load_tsconfig()
    compiler = tsconfig.get("compilerOptions", {})
    assert compiler.get("esModuleInterop", False) is True, (
        "esModuleInterop is not enabled"
    )


# ===========================================================================
# SECTION 5: Environment variables (3 tests)
# ===========================================================================

def test_env_example_exists():
    """.env.example must exist."""
    path = os.path.join(OUTPUT_DIR, ".env.example")
    assert os.path.isfile(path), ".env.example not found"


def test_env_example_has_database_url():
    """".env.example must include DATABASE_URL."""
    content = _read_file(".env.example")
    assert content is not None
    assert "DATABASE_URL" in content, (
        ".env.example does not include DATABASE_URL"
    )


def test_env_example_has_port():
    """.env.example should still include PORT."""
    content = _read_file(".env.example")
    assert content is not None
    assert "PORT" in content, ".env.example does not include PORT"


# ===========================================================================
# SECTION 6: Jest / test runner configuration (4 tests)
# ===========================================================================

def test_jest_configured():
    """Jest configuration must exist (in package.json or jest.config)."""
    pkg = _load_package_json()
    has_jest_in_pkg = "jest" in pkg
    has_jest_config = (
        os.path.isfile(os.path.join(OUTPUT_DIR, "jest.config.js"))
        or os.path.isfile(os.path.join(OUTPUT_DIR, "jest.config.ts"))
        or os.path.isfile(os.path.join(OUTPUT_DIR, "jest.config.json"))
        or os.path.isfile(os.path.join(OUTPUT_DIR, "jest.config.mjs"))
        or os.path.isfile(os.path.join(OUTPUT_DIR, "jest.config.cjs"))
    )
    assert has_jest_in_pkg or has_jest_config, (
        "No Jest configuration found in package.json or as standalone config file"
    )


def test_jest_in_dev_dependencies():
    """Jest (or a compatible test runner) must be in devDependencies."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    has_jest = "jest" in dev_deps
    has_ts_jest = "ts-jest" in dev_deps
    has_vitest = "vitest" in dev_deps
    assert has_jest or has_ts_jest or has_vitest, (
        "No test runner (jest/ts-jest/vitest) found in devDependencies"
    )


def test_types_jest_installed():
    """@types/jest should be in devDependencies."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})
    has_types_jest = "@types/jest" in dev_deps
    has_vitest = "vitest" in dev_deps  # vitest has its own types
    assert has_types_jest or has_vitest, (
        "@types/jest not found in devDependencies"
    )


def test_ts_jest_or_transform_configured():
    """TypeScript test support must be configured (ts-jest, @swc/jest, or vitest)."""
    pkg = _load_package_json()
    dev_deps = pkg.get("devDependencies", {})

    # Check devDependencies
    has_ts_jest = "ts-jest" in dev_deps
    has_swc_jest = "@swc/jest" in dev_deps
    has_vitest = "vitest" in dev_deps

    # Check jest config in package.json
    jest_config = pkg.get("jest", {})
    has_transform = "transform" in jest_config or "preset" in jest_config

    # Check standalone config files
    has_config_file = any(
        os.path.isfile(os.path.join(OUTPUT_DIR, f))
        for f in [
            "jest.config.js", "jest.config.ts", "jest.config.json",
            "jest.config.mjs", "jest.config.cjs",
        ]
    )

    assert (
        has_ts_jest or has_swc_jest or has_vitest
        or has_transform or has_config_file
    ), "No TypeScript test transform configured"


# ===========================================================================
# SECTION 7: Build and test scripts (3 tests)
# ===========================================================================

def test_build_script_exists():
    """package.json must have a 'build' script."""
    pkg = _load_package_json()
    scripts = pkg.get("scripts", {})
    assert "build" in scripts, "package.json has no 'build' script"


def test_test_script_exists():
    """package.json must have a 'test' script."""
    pkg = _load_package_json()
    scripts = pkg.get("scripts", {})
    assert "test" in scripts, "package.json has no 'test' script"


def test_build_script_uses_tsc():
    """Build script should invoke TypeScript compiler."""
    pkg = _load_package_json()
    scripts = pkg.get("scripts", {})
    build = scripts.get("build", "")
    assert "tsc" in build or "typescript" in build or "tsup" in build, (
        f"Build script '{build}' does not invoke TypeScript compiler"
    )


# ===========================================================================
# SECTION 8: Source files unchanged (4 tests)
# ===========================================================================

def test_source_index_unchanged():
    """src/index.ts must be identical to original."""
    original = _read_input_file(os.path.join("src", "index.ts"))
    output = _read_file(os.path.join("src", "index.ts"))
    assert output is not None, "src/index.ts not found in output"
    assert original is not None
    assert output.strip() == original.strip(), (
        "src/index.ts was modified (only config files should change)"
    )


def test_source_server_unchanged():
    """src/server.ts must be identical to original."""
    original = _read_input_file(os.path.join("src", "server.ts"))
    output = _read_file(os.path.join("src", "server.ts"))
    assert output is not None, "src/server.ts not found in output"
    assert original is not None
    assert output.strip() == original.strip(), (
        "src/server.ts was modified (only config files should change)"
    )


def test_source_database_unchanged():
    """src/database.ts must be identical to original."""
    original = _read_input_file(os.path.join("src", "database.ts"))
    output = _read_file(os.path.join("src", "database.ts"))
    assert output is not None, "src/database.ts not found in output"
    assert original is not None
    assert output.strip() == original.strip(), (
        "src/database.ts was modified (only config files should change)"
    )


def test_source_routes_unchanged():
    """src/routes.ts must be identical to original."""
    original = _read_input_file(os.path.join("src", "routes.ts"))
    output = _read_file(os.path.join("src", "routes.ts"))
    assert output is not None, "src/routes.ts not found in output"
    assert original is not None
    assert output.strip() == original.strip(), (
        "src/routes.ts was modified (only config files should change)"
    )


# ===========================================================================
# SECTION 9: All files present (3 tests)
# ===========================================================================

REQUIRED_FILES = [
    "package.json",
    "tsconfig.json",
    os.path.join("src", "index.ts"),
    os.path.join("src", "server.ts"),
    os.path.join("src", "database.ts"),
    os.path.join("src", "routes.ts"),
    os.path.join("tests", "server.test.ts"),
    os.path.join("tests", "database.test.ts"),
    ".env.example",
    "README.md",
]


@pytest.mark.parametrize("rel_path", REQUIRED_FILES)
def test_required_file_exists(rel_path):
    path = os.path.join(OUTPUT_DIR, rel_path)
    assert os.path.isfile(path), f"{rel_path} not found in output"


def test_readme_unchanged():
    """README.md should not be modified."""
    original = _read_input_file("README.md")
    output = _read_file("README.md")
    if original and output:
        assert output.strip() == original.strip(), "README.md was modified"


def test_test_files_unchanged():
    """Test files should not be modified."""
    for test_file in ["tests/server.test.ts", "tests/database.test.ts"]:
        original = _read_input_file(test_file)
        output = _read_file(test_file)
        if original and output:
            assert output.strip() == original.strip(), (
                f"{test_file} was modified (only config files should change)"
            )


# ===========================================================================
# SECTION 10: FIXES.md documentation (3 tests)
# ===========================================================================

def test_fixes_file_exists():
    """FIXES.md must exist documenting the changes."""
    path = os.path.join(OUTPUT_DIR, "FIXES.md")
    assert os.path.isfile(path), "FIXES.md not found in output"


def test_fixes_has_substance():
    """FIXES.md must have meaningful content."""
    content = _read_file("FIXES.md")
    assert content is not None
    assert len(content.strip()) > 100, (
        f"FIXES.md is too short ({len(content.strip())} chars)"
    )


def test_fixes_documents_multiple_issues():
    """FIXES.md should document at least 4 distinct fixes."""
    content = _read_file("FIXES.md") or ""
    # Count structural elements (headings, numbered items, bullets)
    headings = re.findall(r"^#{1,4}\s+.+", content, re.MULTILINE)
    bullets = re.findall(r"^[\-\*]\s+.+", content, re.MULTILINE)
    numbered = re.findall(r"^\d+[\.\)]\s+.+", content, re.MULTILINE)
    total = len(headings) + len(bullets) + len(numbered)
    # Need at least 4 items documenting fixes (we planted 5 issues)
    assert total >= 4, (
        f"FIXES.md documents too few issues ({total} structural items, need >= 4)"
    )
