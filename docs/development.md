Requirements:
* python 3.4
* bower

```bash
# Setup virtual environment
$ virtualenv-3.4 venv
$ source venv/bin/activate
# Install requirements
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
$ bower install
```

# Running the tests
* install the requirements and requirements-dev
* cd into project root
* run `nosetests`

# Generate code coverage
* install the requirements and requirements-dev
* cd into project root
* run `nosetests --with-coverage`
