# For contributing

## Installing environment

Clone the repository.
```bash
git clone git@github.com:esoft-tech/py-bc-configs.git
```

Install poetry using the guide from their website – https://python-poetry.org/docs/#installation.

After installation, apply this in order for poetry to create venv in your project folder.
```bash
poetry config virtualenvs.in-project true
```

Inside project directory install dependencies.
```bash
poetry install
```

Done 🪄 🐈‍⬛ Now you can develop.

## If you want contributing

- Check that ruff passed.
- Check that mypy passed.
- Check that unittests passed.

## If you need to build and publish the package

Up the package version in the `pyproject.toml`.
```diff
- version = "0.1.0"
+ version = "0.1.1"
```

Commit changes and push them to the origin.
```bash
git add pyproject.toml
git commit -m "Up to 0.1.1"
git push
```

Make a tag and push them to the origin.
```bash
git tag 0.1.1
git push origin 0.1.1
```

Build the package.
```bash
poetry build
```

Configurate your pypi token for the poetry.
```bash
poetry config pypi-token.pypi <your-api-token>
```

Publish the package.
```bash
poetry publish
```

**⚠️IMPORTANT⚠️** Make a release with notes about changes.