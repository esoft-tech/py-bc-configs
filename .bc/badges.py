import os
from genbadge import Badge


def run_unittests_and_create_badge():
    if os.system('./.venv/bin/python -m coverage run --omit="*test_*.py" -m unittest '
                 'discover --pattern="*test_*.py"'):
        Badge(left_txt="unittests", right_txt="failed", color="red").write_to(
            "./docs/assets/unittests-badge.svg",
            use_shields=True
        )
    else:
        Badge(left_txt="unittests", right_txt="passed", color="green").write_to(
            "./docs/assets/unittests-badge.svg",
            use_shields=True
        )


def run_coverage_and_create_badge():
    os.system('./.venv/bin/python -m coverage run --omit="*test_*.py" -m unittest '
              'discover --pattern="*test_*.py"')
    os.system('./.venv/bin/python -m coverage report')
    os.system('./.venv/bin/python -m coverage xml')
    os.system('./.venv/bin/genbadge coverage -i coverage.xml -o '
              './docs/assets/coverage-badge.svg')


def run_mypy_and_create_badge():
    if os.system('./.venv/bin/python -m mypy .'):
        Badge(left_txt="mypy", right_txt="failed", color="red").write_to(
            "./docs/assets/mypy-badge.svg",
            use_shields=True
        )
    else:
        Badge(left_txt="mypy", right_txt="passed", color="green").write_to(
            "./docs/assets/mypy-badge.svg",
            use_shields=True
        )


def run_ruff_and_create_badge():
    if os.system('./.venv/bin/python -m ruff check .'):
        Badge(left_txt="Ɍuff", right_txt="failed", color="red").write_to(
            "./docs/assets/ruff-badge.svg",
            use_shields=True
        )
    else:
        Badge(left_txt="Ɍuff", right_txt="passed", color="green").write_to(
            "./docs/assets/ruff-badge.svg",
            use_shields=True
        )


if __name__ == "__main__":
    run_unittests_and_create_badge()
    run_coverage_and_create_badge()
    run_mypy_and_create_badge()
    run_ruff_and_create_badge()
