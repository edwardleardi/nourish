.. role:: file(literal)

.. contributing-start

Contribution Guide
==================

Quick Setup
-----------

Use ``tox``
~~~~~~~~~~~

To start developing, the recommended way is to use ``tox``. This way, your development environment is automatically
prepared by ``tox``, including virtual environment setup, dependency management, installing `nourish` in development mode.

1. Install ``tox``:

   .. code-block:: console

      $ pip install -U -r requirements/tox.txt  # If you are inside a virtual environment, conda environment
      $ pip3 install --user -U -r requirements/tox.txt  # If you are outside any virtual environment or conda environment and don't have tox installed

2. At the root directory of ``nourish``, run:

   .. code-block:: console

      $ tox -e dev

   To force updating development environment in the future, run ``tox --recreate -e dev`` when the development
   environment is not activated.

3. To activate the development environment, run:

   .. code-block:: console

      $ . .tox/dev/bin/activate

Traditional Method
~~~~~~~~~~~~~~~~~~

Alternatively, after cloning this repository (and preferably having created and activated a virtual environment), run
the following command to install all dependencies:

.. code-block:: console

   $ pip install -U -e .

Install all required development packages:

.. code-block:: console

   $ pip install -U -r requirements-dev.txt

Tests & CI
----------

Run All Tests
~~~~~~~~~~~~~

Before and after one stage of development, you may want to try whether the code would pass all tests.

To run all tests on the Python versions that are supported by Nourish and available on your system, run:

.. code-block:: console

   $ tox -s

When you are brave, to force running all tests on all Python versions that are supported by Nourish, run:

.. code-block:: console

   $ tox

By default ``tox`` uses ``virtualenv`` for creating each test environment (such as for each Python version). If you
would prefer ``tox`` to use ``conda``, run:

.. code-block:: console

   $ pip install tox-conda

Running Part of the Tests
~~~~~~~~~~~~~~~~~~~~~~~~~

During development, you likely would like to run only part of the tests to save time.

To run all static tests, run:

.. code-block:: console

   $ tox -e lint

To run all runtime tests on the Python version in the development environment, run:

.. code-block:: console

   $ tox -e py

To run only a specific runtime test, run:

.. code-block:: console

   $ pytest tests -vk [test_name]  # e.g., pytest tests -vk test_default_data_dir

Read `pytest command line document <https://docs.pytest.org/en/stable/usage.html>`__ for its more advanced usage.

To run document generation tests, run:

.. code-block:: console

   $ tox -e docs

Continuous Integration (CI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We prefer keeping CI configuration files, namely :file:`.github/workflows/*` and :file:`.gitlab-ci.yml`, simple and unscrambled.
Normally, only test environment, such as Python version, OS and tox environmental variables, or anything that is
specific to the CI system, such as failure notification. Complicated test dependencies and other test dealings should go
to :file:`tox.ini` and their respective test files in :file:`tests/`.

Development
-----------

Schema vs Schemata
~~~~~~~~~~~~~~~~~~

When creating variables that hold schema information, we use the following naming conventions to minimize confusion between
what we typically refer to as a ``schema``, and what we typically refer to as a ``schemata``:

- **schemata** = refers to the YAML file or the YAML file's full contents
   - A schemata is a YAML file composed of some header information and content in the form of schemas, e.g. the dataset schemata is composed of some header metadata (i.e. ``api_name``, ``name``, and ``last_updated``) and a collection of dataset schemas (i.e. the value returned by the ``datasets`` key).
   - When referring to the YAML file or its full contents, we use ``schemata`` in the name, e.g. ``dataset_schemata``, ``license_schemata``, or ``format_schemata``.

- **schema** = refers to a unit within the YAML file's contents
   - A schema is a unit of the content of a schemata, e.g. the metadata of a particular versioned dataset from a dataset schemata, used to instantiate a ``Dataset`` class.
   - When referring to the schema for a certain (or generic) dataset, license, or format, we use ``schema`` in the name, e.g. ``dataset_schema``, or ``gmb_schema``.
   - Schemas in the plural refers to a dictionary composed of all the schemas in a schemata without the schemata's header information, e.g. ``license_schemas`` would refer to the value returned by the ``licenses`` key from the licenses schemata.

Note: for type checking purposes, both a schema and a schemata in dictionary form can be of custom type ``SchemaDict``

Where to Expose a Symbol (Function, Class, etc.)?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally speaking:

- If a symbol is likely used by a casual user regularly, it should be exposed in :file:`nourish/__init__.py`. This gives
  casual users the cleanest and the most direct access.
- If a symbol is used only by a power user, but is unlikely used by a casual user regularly, it should be exposed in a
  file that does not start with an underscore, such as :file:`nourish/schema.py`; or in the :file:`__init__.py` file in a
  subdirectory that does not start with an underscore, such as :file:`nourish/loaders/__init__.py`. The rationale is that
  the amount of such symbols is usually large and if we expose them at the root level of the package, it would be messy
  and likely confuse casual users.
- If a symbol is solely used for internal purpose, it should be exposed only in files starting with a single underscore,
  such as :file:`nourish/_dataset.py`.

Please keep in mind that the criteria above are not meant to be rigid: They should be applied flexibly in light of
factors such as where existing symbols are placed and other potentially important considerations (if any).

Where to Import a Symbol?
~~~~~~~~~~~~~~~~~~~~~~~~~

When referencing a symbol that is exposed to a user, in general, we prefer importing the symbol from where the package
publicly exposes it over importing from where the source code of the symbol is defined, e.g., use ``from .schema import
SchemaDict`` rather than ``from ._schema import SchemaDict``. This way we have more code paths that would go through
what the user would actually experience and hopefully would give us more chances to discover bugs.

Docs
~~~~

The easiest way to generate the docs is to run the ``tox`` docs test environment. The html index file generates at
:file:`.tox/docs/out/index.html`:

.. code-block:: console

   $ tox -e docs

To run docs tests individually or to generate the docs, cd into the `docs/` directory and run any of the commands below:

.. code-block:: console

   $ cd docs

To generate the HTML files for the docs to the :file:`build` directory (note: this will automatically regenerate the
stubfiles used by :file:`autosummary` prior to generating the html files):

.. code-block:: console

   $ sphinx-build -d build/doctrees source build/html -b html

To check reST code style compliance, run:

.. code-block:: console

   $ rstcheck -r docs/source/miscellaneous docs/source/user_guide docs/source/api-references/*.rst

The reST code style compliance is also checked by the ``tox`` lint test environment if you prefer to use that:

.. code-block:: console

   $ tox -e lint

Dependency Version Pinning Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We should pin the versions of all Python packages that we are using solely for testing and doc generating for a stable
test and doc env (e.g., future incompatibility, regression, etc.). We want to pin these because, in this project, we use
these packages solely for deployment of our development environment (i.e., running tests and generating docs) and we
want stable packages that are used by us for these purposes. We let `Renovate`_ verify that bumping the versions won't
break anything before we actually upgrade any of these dependencies.

We should not pin the actual dependencies of Nourish (as specified in :file:`setup.py`), because Nourish is an intermediate
software layer -- those should be pinned only by the actual deployed application that depends on Nourish. We should only
code the info of supported versions of these dependencies. If there is some regression or incompatibilities in the
latest versions of our dependencies, we should either work around them, or update :file:`setup.py` to avoid depending on
those versions.

.. _Renovate: https://github.com/apps/renovate

Releases & Publishing to PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make a new release:

- Tag the commit following `PEP 0440 <https://www.python.org/dev/peps/pep-0440>`__, e.g. ``git tag -a v0.1a1 -m "First Alpha Release"``.
- Push the tag, e.g. ``git push origin v0.1a1``.
- On the `GitHub Releases <https://github.com/edwardleardi/nourish/releases>`__ page, convert the tag into a release by adding a title, description, and marking whether or not it is a pre-release.

To publish to PyPI:

- When a full release (not a pre-release) is published, :file:`.github/workflows/publish-to-pypi.yml` will automatically upload the release to PyPI.
- However to manually upload a release, run ``python setup.py sdist bdist_wheel`` then ``twine upload -r pypi dist/nourish-x.x*``.

Pull Request & Issues
---------------------

Developer's Certificate of Origin (DCO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To ensure licensing criteria are followed, Nourish requires all contributors to agree to the Developer Certificate of Origin
(DCO). The DCO is an attestation attached to every contribution made by every developer. In the commit message of the
contribution, the developer simply adds a ``Signed-off-by: Name <Email>`` statement and thereby agrees to the DCO. 

The DCO is a commitment that the contributor has the right to submit the patch per the license. The DCO agreement can be found
at `http://developercertificate.org/ <http://developercertificate.org/>`__.

The DCO sign-off can either be added manually to your commit body, or you can add either ``-s`` or ``--signoff`` to your usual
Git commit commands. If you forget to add the sign-off you can amend a previous commit with the sign-off by running
``git commit --amend -s``.
