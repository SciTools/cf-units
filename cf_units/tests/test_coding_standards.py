# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.

import subprocess
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

import pytest

import cf_units

LICENSE_TEMPLATE = """# Copyright cf-units contributors
#
# This file is part of cf-units and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details."""


REPO_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_DIR / "docs"
DOCS_DIR = Path(
    cf_units.config.get_option("Resources", "doc_dir", default=DOCS_DIR)
)
exclusion = ["Makefile", "make.bat", "build"]
DOCS_DIRS = DOCS_DIR.glob("*")
DOCS_DIRS = [DOC_DIR for DOC_DIR in DOCS_DIRS if DOC_DIR.name not in exclusion]
IS_GIT_REPO = (REPO_DIR / ".git").is_dir()


@pytest.mark.skipif(not IS_GIT_REPO, reason="Not a git repository.")
class TestLicenseHeaders:
    @staticmethod
    def whatchanged_parse(whatchanged_output):
        """
        Returns a generator of tuples of data parsed from
        "git whatchanged --pretty='TIME:%at'". The tuples are of the form
        ``(filename, last_commit_datetime)``

        Sample input::

            ['TIME:1366884020', '',
             ':000000 100644 0000000... 5862ced... A\tcf_units/cf_units.py']

        """
        dt = None
        for line in whatchanged_output:
            if not line.strip():
                continue
            elif line.startswith("TIME:"):
                dt = datetime.fromtimestamp(int(line[5:]))
            else:
                # Non blank, non date, line -> must be the lines
                # containing the file info.
                fname = " ".join(line.split("\t")[1:])
                yield fname, dt

    @staticmethod
    def last_change_by_fname():
        """
        Return a dictionary of all the files under git which maps to
        the datetime of their last modification in the git history.

        .. note::

            This function raises a ValueError if the repo root does
            not have a ".git" folder. If git is not installed on the system,
            or cannot be found by subprocess, an IOError may also be raised.

        """
        # Call "git whatchanged" to get the details of all the files and when
        # they were last changed.
        output = subprocess.check_output(
            ["git", "whatchanged", "--pretty=TIME:%ct"], cwd=REPO_DIR
        )
        output = str(output.decode("ascii"))
        output = output.split("\n")
        res = {}
        for fname, dt in TestLicenseHeaders.whatchanged_parse(output):
            if fname not in res or dt > res[fname]:
                res[fname] = dt

        return res

    def test_license_headers(self):
        exclude_patterns = (
            "setup.py",
            "build/*",
            "dist/*",
            "cf_units/_version.py",
            "cf_units/_udunits2_parser/parser/*",
        )

        last_change_by_fname = self.last_change_by_fname()

        failed = False
        for fname in sorted(last_change_by_fname):
            full_fname = REPO_DIR / fname
            if (
                full_fname.suffix == ".py"
                and full_fname.is_file()
                and not any(fnmatch(fname, pat) for pat in exclude_patterns)
            ):
                with open(full_fname) as fh:
                    content = fh.read()
                    if not content.startswith(LICENSE_TEMPLATE):
                        print(
                            f"The file {fname} does not start with the "
                            f"required license header."
                        )
                        failed = True

        if failed:
            raise AssertionError(
                "There were license header failures. See stdout."
            )


@pytest.mark.skipif(not IS_GIT_REPO, reason="Not a git repository.")
def test_python_versions():
    """Confirm alignment of ALL files listing supported Python versions."""
    supported = ["3.10", "3.11", "3.12"]
    supported_strip = [ver.replace(".", "") for ver in supported]
    supported_latest = supported_strip[-1]

    workflows_dir = REPO_DIR / ".github" / "workflows"

    # Places that are checked:
    pyproject_toml_file = REPO_DIR / "pyproject.toml"
    setup_cfg_file = REPO_DIR / "setup.cfg"
    tox_file = REPO_DIR / "tox.ini"
    ci_locks_file = workflows_dir / "ci-locks.yml"
    ci_tests_file = workflows_dir / "ci-tests.yml"
    ci_wheels_file = workflows_dir / "ci-wheels.yml"

    text_searches: list[tuple[Path, str]] = [
        (
            pyproject_toml_file,
            "target-version = ["
            + ", ".join([f'"py{p}"' for p in supported_strip])
            + "]",
        ),
        (
            setup_cfg_file,
            "\n    ".join(
                [
                    f"Programming Language :: Python :: {ver}"
                    for ver in supported
                ]
            ),
        ),
        (
            tox_file,
            "[testenv:py{" + ",".join(supported_strip) + "}-lock]",
        ),
        (
            tox_file,
            "[testenv:py{"
            + ",".join(supported_strip)
            + "}-{linux,osx,win}-test]",
        ),
        (
            ci_locks_file,
            "lock: ["
            + ", ".join([f"py{p}-lock" for p in supported_strip])
            + "]",
        ),
        (
            ci_tests_file,
            (
                f"os: [ubuntu-latest]\n"
                f"{8*' '}version: ["
                + ", ".join([f"py{p}" for p in supported_strip])
                + "]"
            ),
        ),
        (
            ci_tests_file,
            (f"os: ubuntu-latest\n" f"{12*' '}version: py{supported_latest}"),
        ),
        (
            ci_tests_file,
            (f"os: macos-latest\n" f"{12*' '}version: py{supported_latest}"),
        ),
    ]

    # This routine will not check for file existence first - if files are
    #  being added/removed we want developers to be aware that this test will
    #  need to be updated.
    for path, search in text_searches:
        assert search in path.read_text()

    tox_text = tox_file.read_text()
    for version in supported_strip:
        # A fairly lazy implementation, but should catch times when the
        #  section header does not match the conda_spec for the `tests`
        #  section. (Note that Tox does NOT provide its own helpful
        #  error in these cases).
        py_version = f"py{version}"
        assert tox_text.count(f"    {py_version}-") == 3
        assert tox_text.count(f"{py_version}-lock") == 3

    ci_wheels_text = ci_wheels_file.read_text()
    cibw_line = next(
        line for line in ci_wheels_text.splitlines() if "CIBW_SKIP" in line
    )
    assert all([p not in cibw_line for p in supported_strip])
