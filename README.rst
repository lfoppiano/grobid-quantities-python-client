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

The client can be installed using `pip`::

  pip install grobid-quantities-client

Command Line Interface (CLI)
----------------------------

The CLI follows the following parameters::

    python -m grobid_quantities.quantities --help
    usage: quantities.py [-h] --input INPUT [--output OUTPUT] [--base-url BASE_URL] [--config CONFIG] [--n N] [--force] [--verbose]

    Client for the Grobid-quantities service

    optional arguments:
      -h, --help           show this help message and exit
      --input INPUT        path to the directory containing PDF files or .txt (for processCitationList only, one reference per line) to process
      --output OUTPUT      path to the directory where to put the results (optional)
      --base-url BASE_URL  Base url of the service (without the suffix `/service/`)
      --n N                concurrency for service usage
      --force              force re-processing pdf input files when tei output files already exist



API Usage
---------
Initialisation::

    from grobid_quantities.quantities import Quantities
    client = QuantitiesAPI(base_url=http(s)://server_url:port/base/url)


Process raw text::

    client.process_text(
        "I lost two minutes"
    )

Process PDF document::

    client.process_pdf(pdfFile)


Parse the measurements::

    client.parse_measures("from": "10", "to": "20", "unit": "km")


The response is a tuple where the first element is the status code and and the second element the response body as a dictionary.
Here an example::

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