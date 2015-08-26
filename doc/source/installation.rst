.. _install:

Installation
============

This part of the documentation covers the installation of rtcclient.
The first step to using any software package is getting it properly installed.


Distribute & Pip
----------------

Installing rtcclient is simple with `pip <https://pip.pypa.io>`_, just run
this in your terminal::

    $ pip install rtcclient

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install rtcclient


Get from the Source Code
------------------------

RTCClient is actively developed on GitHub, where the code is
`always available <https://github.com/dixudx/rtcclient>`_.

You can either clone the public repository and checkout released tags
(e.g. tag 0.1.dev95)::

    $ git clone git://github.com/dixudx/rtcclient.git
    $ cd rtcclient
    $ git checkout tags/0.1.dev95

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install
