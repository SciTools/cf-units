# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.

from fnmatch import fnmatch
from pathlib import Path
import subprocess

from packaging.version import Version
import pytest
import tomli

import cf_units

LICENSE_TEMPLATE = """# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details."""


REPO_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_DIR / "docs"
DOCS_DIR = Path(cf_units.config.get_option("Resources", "doc_dir", default=DOCS_DIR))
exclusion = ["Makefile", "make.bat", "build"]
DOCS_DIRS = DOCS_DIR.glob("*")
DOCS_DIRS = [DOC_DIR for DOC_DIR in DOCS_DIRS if DOC_DIR.name not in exclusion]
IS_GIT_REPO = (REPO_DIR / ".git").is_dir()


@pytest.mark.skipif(not IS_GIT_REPO, reason="Not a git repository.")
class TestLicenseHeaders:
    class NongitError(ValueError):
        pass

    @classmethod
    def all_git_filepaths(cls):
        """Return a list of all the files under git."""
        output = subprocess.check_output(
            ["git", "ls-files"],
            cwd=REPO_DIR,
        )

        # Result has one file-path per line.
        output_lines = output.decode("ascii").split("\n")
        # Strip off any leading+trailing whitespace.
        output_lines = [line.strip() for line in output_lines]
        # Ignore blank lines.
        output_lines = [line for line in output_lines if len(line) > 0]
        return output_lines

    def test_license_headers(self):
        exclude_patterns = (
            "setup.py",
            "build/*",
            "dist/*",
            "cf_units/_version.py",
            "cf_units/_udunits2_parser/parser/*",
            "cf_units/_udunits2_parser/_antlr4_runtime/*",
        )

        file_paths = self.all_git_filepaths()

        failed = False
        for fname in sorted(file_paths):
            full_fname = REPO_DIR / fname
            if (
                full_fname.suffix == ".py"
                and full_fname.is_file()
                and not any(fnmatch(fname, pat) for pat in exclude_patterns)
            ):
                with open(full_fname, encoding="utf-8") as fh:
                    content = fh.read()
                    if not content.startswith(LICENSE_TEMPLATE):
                        print(
                            f"The file {fname} does not start with the "
                            f"required license header."
                        )
                        failed = True

        if failed:
            raise AssertionError("There were license header failures. See stdout.")


@pytest.mark.skipif(not IS_GIT_REPO, reason="Not a git repository.")
def test_python_versions():
    """Confirm alignment of ALL files listing supported Python versions."""
    supported = ["3.10", "3.11", "3.12", "3.13"]
    supported_strip = [ver.replace(".", "") for ver in supported]
    _parsed = [Version(v) for v in supported]
    supported_latest = str(max(_parsed)).replace(".", "")

    workflows_dir = REPO_DIR / ".github" / "workflows"

    # Places that are checked:
    pyproject_toml_file = REPO_DIR / "pyproject.toml"
    ci_locks_file = workflows_dir / "ci-locks.yml"
    ci_tests_file = workflows_dir / "ci-tests.yml"
    ci_wheels_file = workflows_dir / "ci-wheels.yml"

    text_searches: list[tuple[Path, str]] = [
        (
            pyproject_toml_file,
            "\n    ".join(
                [f'"Programming Language :: Python :: {ver}",' for ver in supported]
            ),
        ),
        (
            pyproject_toml_file,
            f'requires-python = ">={min(_parsed)}"',
        ),
        (
            ci_locks_file,
            f'NAME: "cf-units-py{supported_latest}"',
        ),
        (
            ci_tests_file,
            (
                f"os: [ubuntu-latest]\n"
                f"{8 * ' '}version: ["
                + ", ".join([f"py{p}" for p in supported_strip])
                + "]"
            ),
        ),
        (
            ci_tests_file,
            (f"os: ubuntu-latest\n{12 * ' '}version: py{supported_latest}"),
        ),
        (
            ci_tests_file,
            (f"os: macos-latest\n{12 * ' '}version: py{supported_latest}"),
        ),
    ]

    # This routine will not check for file existence first - if files are
    #  being added/removed we want developers to be aware that this test will
    #  need to be updated.
    for path, search in text_searches:
        assert search in path.read_text()

    ci_wheels_text = ci_wheels_file.read_text()
    (cibw_line,) = (line for line in ci_wheels_text.splitlines() if "CIBW_SKIP" in line)
    assert all(p not in cibw_line for p in supported_strip)

    with pyproject_toml_file.open("rb") as f:
        data = tomli.load(f)
    pixi_envs = data.get("tool", {}).get("pixi", {}).get("environments", {})
    for version in supported_strip:
        py_version = f"py{version}"
        assert py_version in pixi_envs
        assert [k.endswith(py_version) for k in pixi_envs].count(True) == 5
