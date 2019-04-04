Python client for Grobid Quantities
===================================

.. image:: http://img.shields.io/:license-apache-blue.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html

.. image:: https://travis-ci.org/hirmeos/entity-fishing-client-python.svg?branch=master
   :target: https://travis-ci.org/hirmeos/entity-fishing-client-python


Python client to query the `Grobid Quantities service API`_
For more information about Grobid Quantities, please check the `Grobid Quantities Documentation`_.

.. _Grobid Quantities service API: http://github.com/kermitt2/grobid-quantities
.. _Grobid Quantities Documentation: http://nerd.readthedocs.io


Installation
------------

The client can be installed using `pip`:

   pip install grobid-quantities-python

Usage
-----

Process Text / PDF
##################

.. code-block:: python

    from grobid.quantities import QuantitiesClient
    client = QuantitiesClient(apiBase=server_url)


To process raw text:

.. code-block:: python

    client.process_text(
        "I lost two minutes"
    )

To process PDF

.. code-block:: python

    client.process_pdf(pdfFile)


To parse the measurements

.. code-block:: python

    client.parse_measures("from": "10", "to": "20", "unit": "km")



The response is a tuple where the first element is the status code and and the second element the response body as a dictionary.
Here an example: 

.. code-block:: python

    (
        200,
        {
          "runtime": 123,
          "measurements": [
            {
              "type": "value",
              "quantity": {
                "type": "time",
                "rawValue": "two",
                "rawUnit": {
                  "name": "minutes",
                  "type": "time",
                  "system": "non SI",
                  "offsetStart": 11,
                  "offsetEnd": 18
                },
                "parsedValue": {
                  "numeric": 2,
                  "structure": {
                    "type": "ALPHABETIC",
                    "formatted": "two"
                  },
                  "parsed": "two"
                },
                "normalizedQuantity": 120,
                "normalizedUnit": {
                  "name": "s",
                  "type": "time",
                  "system": "SI base"
                },
                "offsetStart": 7,
                "offsetEnd": 11
              }
            }
          ]
        }
   )

Batch processing
######################
The batch processing is implemented in the class ``QuantitiesBatch``.
The class can be instantiated by defining the entity-fishing url in the constructor, else the default one is used.

To run the processing, the method `process` requires the `input` directory, a callback and the number of threads/processes.
There is an already ready implementation in `script/batchSample.py`.

To run it:
 - under this work branch, prepare two folders: `input` which containing the input PDF files to be processed and `output` which collecting the processing result
 - we recommend to create a new virtualenv, activate it and install all the requirements needed in this virtual environment using `$ pip install -r /path/of/grobid-quantities-python-client/source/requirements.txt`
 - (temporarly, until this branch is not merged) install entity-fishing **multithread branch** in edit mode (`pip install -e /path/of/client-python/source`)
 - run it with `python runFile.py input output 5`
