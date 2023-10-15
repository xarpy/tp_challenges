# TP Challenges

[![Python Version][python-image]][python-url]


A collection of interesting challenges to improve technical skills and test new skills

## Installation

### Environment Local

Using your dependency manager, create a python environment, follow a [link](https://ahmed-nafies.medium.com/pip-pipenv-poetry-or-conda-7d2398adbac9) talking about the managers!

Access the project folder and using the **pip** manager, inside the python env, apply the command below:

Upgrade pip version and install requirements and install:

```sh
pip install --upgrade pip && pip install --require-hashes -r requirements/dev.txt
```
After installing all dependencies,compile this project with command:

```sh
python -m spacy download en_core_web_sm && playwright install
```

And to run each script, just use the command below:
```sh
python -m scripts.<module-you-want-test>
```

### Docker Build

You will need to have docker compose, and finally apply the command:

```sh
docker compose up --build
```

After build project, in another terminal, apply the command:

```sh
docker exec -it telescopes python -m scripts.<module-you-want-test>
```


**Obs:**

* For practical use of the application it is necessary to add single quotes, making it a valid argument.
* the search_engine script was tested with an exact file search argument.
* We recommend creating the credentials for using the search_engine script in the examples folder, otherwise it won't work with the name `google-drive.json`.


## Dependencies

This project uses hashed dependencies. To update them, edit `requirements/base.in` for project dependencies and `requirements/dev.in` for development dependencies and run:
```sh
pip-compile --generate-hashes --output-file requirements/base.txt requirements/base.in && \
pip-compile --generate-hashes --output-file requirements/dev.txt requirements/dev.in
```
It is always necessary to `pip-compile` both because dev-deps references base-deps.

## Usage

In order to be able to normalize, we add the best practices in this project, aiming to respect the principles with example **Clean Code**, **SOLID** and others. For more details, see the tip links!


### Formatters and Linters

* [Flake8](https://flake8.pycqa.org/en/latest/index.html)
* [Black](https://black.readthedocs.io/en/stable/)
* [Isort](https://isort.readthedocs.io/en/latest/)
* [Bandit](https://bandit.readthedocs.io/en/latest/)
* [MyPy](https://mypy.readthedocs.io/en/stable/)

**Obs:**

* Programming with Python, we use the `snake_case` style for variables, functions and methods, and the `PascalCase` style for classes. Configuration variables should written in `UPPERCASE`.

### Structure

We use the **microservices architecture patterns** with **DDD principle**, to create system resources. To example, see the content:

```sh
./
├── examples/
│   ├── companies_linkedin.csv
│   └──  g2_urls.csv
├── requirements/
│   ├── base.in
│   ├── base.txt
│   ├── dev.in
│   └── dev.txt
├── scripts/
│   ├──company_details.py
│   ├── count_employees.py
│   ├── __init__.py
│   └──search_engine.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── env.example
├── LICENSE
├── pyproject.toml
└── README.md

```

### Tests

In this application, we used this dependencies to perform, scan and cover tests in the application:

* [Interrogate](https://interrogate.readthedocs.io/en/latest/)
* [Coverage](https://coverage.readthedocs.io/en/7.3.2/)
* [Pytest](https://docs.pytest.org/en/7.4.x/)

In this application, unit tests were created, using **pytest**. Follow the instructions to run the tests:

* To see tests list

```sh
pytest test -co
```

* To run all test

```sh
pytest .
```

* To run only test module

```sh
pytest -vv test/<test-script-you-want-test>.py
```

* To run only function test module

```sh
pytest -vv test/<test-script-you-want-test>.py::<name-of-function-you-want-test>
```

**Obs:**

* Any doubts about the use or how pytest works, in the resources section we provide a direct link to the tool's documentation.


## Resources and Documentations

* [Pip (Package Installer Python)](https://pip.pypa.io/en/stable/)
* [Pre-commits](https://pre-commit.com/index.html)
* [Editor Config](https://editorconfig.org/)
* [Pip Tools](https://github.com/jazzband/pip-tools)
* [Click](https://click.palletsprojects.com/en/8.1.x/)
* [Docker](https://docs.docker.com/get-started/)
* [Docker Compose](https://docs.docker.com/compose/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

[python-url]: https://www.python.org/dev/peps/pep-0596/
[python-image]: https://img.shields.io/badge/python-v3.10-blue
