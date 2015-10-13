Requirements:
* python 3.5
* bower

```bash
# Setup virtual environment
virtualenv-3.5 venv
source venv/bin/activate
# Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt
bower install
```

Here's how to set up `bsAbstimmungen` for local development.

1. Fork the [raphiz/bsAbstimmungen][repo] repo on GitHub

2. Clone your fork locally:

 ```bash
 $ git clone git@github.com:<your github username>/bsAbstimmungen.git
 ```

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development:

 ```bash
 $ cd bsAbstimmungen/
 $
 $ pip install --editable .
 ```

4. Create a branch for local development:

 ```bash
 $ git checkout -b name-of-your-bugfix-or-feature
 ```

5. Make you changes locally

6. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox:

 ```bash
 $ flake8 bsAbstimmungen tests
 $ invoke test
 $ tox
 ```

 To get flake8 and tox, just pip install them into your virtualenv.

7. Commit your changes and push your branch to GitHub:

 ```bash
 $ git add .
 $ git commit -m "Detailed description of your changes."
 $ git push origin name-of-your-bugfix-or-feature
 ```

8. Check that the test coverage hasn't dropped:

   ```bash
   $ invoke coverage
   ```

9. Submit a pull request through the GitHub website. I would encourage you to submit your pull request early in the process. This makes it easier to maintain an overview of current development and opens up for continous discussion.
