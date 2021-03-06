fpylll
======

A Python (2 and 3) wrapper for `fplll <https://github.com/dstehle/fplll>`_.

.. image:: https://travis-ci.org/malb/fpylll.svg?branch=master
    :target: https://travis-ci.org/malb/fpylll

.. code-block:: python

    >>> from fpylll import *
   
    >>> A = IntegerMatrix(50, 50)
    >>> A.randomize("ntrulike", bits=50, q=127)
    >>> A[0].norm()
    3564748886669202.5

    >>> M = GSO.Mat(A)
    >>> M.update_gso()
    >>> M.get_mu(1,0)
    0.815748944429783

    >>> L = LLL.Reduction(M)
    >>> L()
    >>> M.get_mu(1,0)
    0.41812865497076024
    >>> A[0].norm()
    24.06241883103193

The basic BKZ algorithm can be implemented in about 60 pretty readable lines of Python code (cf. `simple_bkz.py <https://github.com/malb/fpylll/blob/master/src/fpylll/contrib/simple_bkz.py>`_).
             
Requirements
------------

fpylll relies on the following C/C++ libraries:

- `GMP <https://gmplib.org>`_ or `MPIR <http://mpir.org>`_ for arbitrary precision integer arithmetic.
- `MPFR <http://www.mpfr.org>`_ for arbitrary precision floating point arithmetic.
- `QD <http://crd-legacy.lbl.gov/~dhbailey/mpdist/>`_ for double double and quad double arithmetic (optional).
- `fpLLL <https://github.com/dstehle/fplll>`_ for pretty much everything.

fpylll also relies on

- `Cython <http://cython.org>`_ for linking Python and C/C++.
- `cysignals <https://github.com/sagemath/cysignals>`_ for signal handling such as interrupting C++ code.
- `py.test <http://pytest.org/latest/>`_ for testing Python.
- `flake8 <https://flake8.readthedocs.org/en/latest/>`_ for linting.

We also suggest

- `IPython  <https://ipython.org>`_ for interacting with Python
- `Numpy <http://www.numpy.org>`_ for numerical computations (e.g. with Gram-Schmidt values)

Getting Started
---------------

We recommend `virtualenv <https://virtualenv.readthedocs.org/>`_ for isolating Python build environments and `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/>`_ to manage virtual environments.

1. Create a new virtualenv and activate it:

   .. code-block:: bash

     $ virtualenv env
     $ source ./env/bin/activate

We indicate active virtualenvs by the prefix ``(fpylll)``.

2. Install the required libraries – `GMP <https://gmplib.org>`_ or `MPIR <http://mpir.org>`_ and `MPFR <http://www.mpfr.org>`_  – if not available already. You may also want to install `QD <http://crd-legacy.lbl.gov/~dhbailey/mpdist/>`_.

3. Install fplll:

   .. code-block:: bash

     $ (fpylll) ./install-dependencies.sh $VIRTUAL_ENV

4. Then, execute:

   .. code-block:: bash

     $ (fpylll) pip install Cython
     $ (fpylll) pip install -r requirements.txt

to install the required Python packages (see above).

5. If you are so inclined, run:

   .. code-block:: bash

     $ (fpylll) pip install -r suggestions.txt

to install suggested Python packages as well (optional).

6. Build the Python extension:

   .. code-block:: bash

     $ (fpylll) export PKG_CONFIG_PATH="$VIRTUAL_ENV/lib/pkgconfig:$PKG_CONFIG_PATH"
     $ (fpylll) python setup.py build_ext
     $ (fpylll) python setup.py install

7. To run fpylll, you will need to:

   .. code-block:: bash

     $ (fpylll) export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib"

so that Python can find fplll and friends.

8. Start Python:

   .. code-block:: bash

    $ (fpylll) ipython

To reactivate the virtual environment later, simply run:

   .. code-block:: bash

    $ source ./env/bin/activate

Note that you can also patch ``activate`` to set ``LD_LIBRRY_PATH``. For this, add:

.. code-block:: bash

    ### LD_LIBRARY_HACK
    _OLD_LD_LIBRARY_PATH="$LD_LIBRARY_PATH"
    LD_LIBRARY_PATH="$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH"
    export LD_LIBRARY_PATH
    ### END_LD_LIBRARY_HACK

    ### PKG_CONFIG_HACK
    _OLD_PKG_CONFIG_PATH="$PKG_CONFIG_PATH"
    PKG_CONFIG_PATH="$VIRTUAL_ENV/lib/pkgconfig:$PKG_CONFIG_PATH"
    export PKG_CONFIG_PATH
    ### END_PKG_CONFIG_HACK

towards the end and:

.. code-block:: bash

    ### LD_LIBRARY_HACK
    if ! [ -z ${_OLD_LD_LIBRARY_PATH+x} ] ; then
        LD_LIBRARY_PATH="$_OLD_LD_LIBRARY_PATH"
        export LD_LIBRARY_PATH
        unset _OLD_LD_LIBRARY_PATH
    fi
    ### END_LD_LIBRARY_HACK

    ### PKG_CONFIG_HACK
    if ! [ -z ${_OLD_PKG_CONFIG_PATH+x} ] ; then
        PKG_CONFIG_PATH="$_OLD_PKG_CONFIG_PATH"
        export PKG_CONFIG_PATH
        unset _OLD_PKG_CONFIG_PATH
    fi
    ### END_PKG_CONFIG_HACK

in the ``deactivate`` function in the ``activate`` script.

Contributing
------------

To contribute to fpylll, clone this repository, commit your code on a separate branch and send a pull request. Please write tests for your code. You can run them by calling::

    $ (fpylll) py.test

from the top-level directory which runs all tests in ``tests/test_*.py``. We run `flake8 <https://flake8.readthedocs.org/en/latest/>`_ on every commit automatically, In particular, we run::

    $ (fpylll) flake8 --max-line-length=120 --max-complexity=16 --ignore=E22,E241 src

Note that fpylll supports Python 2 and 3. In particular, tests are run using Python 2.7 and 3.5. See `.travis.yml <https://github.com/malb/fpylll/blob/master/.travis.yml>`_ for details on automated testing.

Attribution & License
---------------------

We copied a decent bit of code over from Sage, mostly from it’s fpLLL interface.

fpylll is licensed under the GPLv2+.  
