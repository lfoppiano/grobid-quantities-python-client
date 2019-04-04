import sys

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from zenlog import logging

from grobid.client import ApiClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '\n\n %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
stream.setFormatter(formatter)
logger.addHandler(stream)


class QuantitiesClient(ApiClient):
    api_base = "http://localhost:8060/service"
    max_text_length = 500  # Approximation.
    sentences_per_group = 10  # Number of sentences per group

    def __init__(self, apiBase=api_base):
        super(QuantitiesClient, self).__init__(base_url=apiBase)
        if not apiBase.endswith('/'):
            apiBase = apiBase + '/'
        api_base = apiBase

        self.process_pdf_url = urljoin(api_base, "annotateQuantityPDF")
        self.process_text_url = urljoin(api_base, "processQuantityText")
        self.parse_measures_url = urljoin(api_base, "parseMeasure")

    def process_pdf(self, file):

        files = {
            'file': (
                file,
                open(file, 'rb'),
                'application/pdf',
                {'Expires': '0'}
            )
        }

        res, status = self.post(
            self.process_pdf_url,
            files=files,
            headers={'Accept': 'application/json'},
        )

        if status == 200:
            return status, self.decode(res)
        else:
            logger.debug('Quantitiers PDF extraction failed with error ' + str(status))
            return status, None

    def process_text(self, text):
        files = {'text': str(text)}

        res, status = self.post(
            self.process_text_url,
            files=files,
            headers={'Accept': 'application/json'},
        )

        if status == 200:
            return status, self.decode(res)
        else:
            logger.debug('Disambiguation failed.')
            return status, None

    def parse_measures(self, text):
        res, status_code = self.post(self.parse_measures_url, data=text)

        if status_code == 200:
            return status_code, self.decode(res)
        else:
            logger.debug("Request failed")
            # if 'description' in res:
            #     logger.debug("Error: " + res['description']);
            return status_code, None
