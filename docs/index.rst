.. _index:

sgfs
=========

This Python package is a translation layer between `Shotgun <http://www.shotgunsoftware.com/>`_ entities and a file structure on disk. In general, its overarching tasks are to:

- map Shotgun entities to their canonical path on disk;
- map paths on disk to the coresponding Shotgun entities;
- create new structures on disk;
- indentify existing structures on disk for use in above translation.


Contents
--------

.. toctree::
    :maxdepth: 2
    
    sgfs
    context
    cache


.. todo:: Document thoroughly:

    - Context graphs
    - Schema configuration
    - Schema graphs
    - Structure graphs
    - ``.sgfs.yml`` tags
    - reverse cache
    - ``SGFS`` API
    - ``Context`` API
    - ``PathCache`` API


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
