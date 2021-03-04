.. role:: file(literal)
.. role:: func(literal)

.. readme-start

Nourish (Under Development)
===========================

.. image:: https://img.shields.io/pypi/v/nourish.svg
   :target: https://pypi.python.org/pypi/nourish
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/nourish
   :target: https://pypi.python.org/pypi/nourish
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/implementation/nourish
   :target: https://pypi.python.org/pypi/nourish
   :alt: PyPI - Implementation

.. image:: https://badges.gitter.im/edwardleardi/nourish.svg
   :target: https://gitter.im/edwardleardi/nourish
   :alt: Gitter

.. image:: https://github.com/edwardleardi/nourish/workflows/Runtime%20Tests/badge.svg
   :target: https://github.com/edwardleardi/nourish/commit/main
   :alt: Runtime Tests

.. image:: https://github.com/edwardleardi/nourish/workflows/Lint/badge.svg
   :target: https://github.com/edwardleardi/nourish/commit/main
   :alt: Lint

.. image:: https://github.com/edwardleardi/nourish/workflows/Docs/badge.svg
   :target: https://github.com/edwardleardi/nourish/commit/main
   :alt: Docs

.. image:: https://github.com/edwardleardi/nourish/workflows/Development%20Environment/badge.svg
   :target: https://github.com/edwardleardi/nourish/commit/main
   :alt: Development Environment

Nourish is a Python API that enables data consumers and distributors to easily use and share datasets, and establishes a
standard for exchanging data assets. It enables:

- a data scientist to have a simpler and more unified way to begin working with a wide range of datasets, and
- a data distributor to have a consistent, safe, and open source way to share datasets with interested communities.

.. sidebar:: Quick Example

   .. code-block:: python

      >>> import nourish
      >>> nourish.list_all_datasets()
      {'claim_sentences_search': ('1.0.2',),
       ..., 'wikitext103': ('1.0.1',)}
      >>> nourish.load_dataset('wikitext103')
      {...}  # Content of the dataset

Install the Package & its Dependencies
--------------------------------------

.. TODO: Prior to the first release, replace this section with installing from pypi

To install the latest version of Nourish, run

.. code-block:: console

   $ pip install -U git+https://github.com/edwardleardi/nourish

Alternatively, if you have downloaded the source, switch to the source directory (same directory as this README file,
``cd /path/to/nourish-source``) and run

.. code-block:: console

   $ pip install -U .

Quick Start
-----------

Import the package and load a dataset. Nourish will download `WikiText-103
<https://developer.ibm.com/exchanges/data/all/wikitext-103/>`__ dataset (version ``1.0.1``) if it's not already
downloaded, and then load it.

.. code-block:: python

   import nourish
   wikitext103_data = nourish.load_dataset('wikitext103')

View available Nourish datasets and their versions.

.. code-block:: python

   >>> nourish.list_all_datasets()
   {'claim_sentences_search': ('1.0.2',), ..., 'wikitext103': ('1.0.1',)}

To view your globally set configs for Nourish, such as your default data directory, use :func:`nourish.get_config`.

.. code-block:: python

   >>> nourish.get_config()
   Config(DATADIR=PosixPath('dir/to/dowload/load/from'), ..., DATASET_SCHEMA_URL='file/to/load/datasets/from')

By default, :func:`nourish.load_dataset` downloads to and loads from
:file:`~/.nourish/data/<dataset-name>/<dataset-version>/`. To change the default data directory, use :func:`nourish.init`.

.. code-block:: python

   nourish.init(DATADIR='new/dir/to/dowload/load/from')

Load a previously downloaded dataset using :func:`nourish.load_dataset`. With the new default data dir set, Nourish now
searches for the `Groningen Meaning Bank <https://developer.ibm.com/exchanges/data/all/groningen-meaning-bank/>`__
dataset (version ``1.0.2``) in :file:`new/dir/to/dowload/load/from/gmb/1.0.2/`.

.. code-block:: python

   gmb_data = load_dataset('gmb', version='1.0.2', download=False)  # assuming GMB dataset was already downloaded

Notebooks
---------

For a more extensive look at Nourish functionality, check out these notebooks:

* `Early Nourish Features Walkthrough <https://github.com/edwardleardi/nourish/blob/main/docs/notebooks/nourish-mvp-demo.ipynb>`__
