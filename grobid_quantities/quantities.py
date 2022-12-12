import argparse
import json
import ntpath
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time
from os.path import isfile, join, splitext

import requests

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from zenlog import logging

from grobid_quantities.client import ApiClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '\n\n %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
stream.setFormatter(formatter)
logger.addHandler(stream)


class ServerUnavailableException(Exception):
    pass


class QuantitiesAPI(ApiClient):
    default_base_url = "http://localhost:8060/service"
    max_text_length = 500  # Approximation.
    sentences_per_group = 10  # Number of sentences per group
    config_path = None

    def __init__(self, base_url=default_base_url,
                 sleep_time=5,
                 timeout=60,
                 config_path=None,
                 check_server=True):

        super(QuantitiesAPI, self).__init__(base_url=base_url)
        if not self.base_url.endswith('/'):
            self.base_url = self.base_url + '/'

        self.base_url += 'service/'

        if check_server:
            self._test_server_connection(self.base_url)

        self.timeout = timeout
        self.sleep_time = sleep_time

        # if config_path is not None:
        #     self.config_path = self._load_config(config_path)

        self.process_pdf_url = urljoin(self.base_url, "annotateQuantityPDF")
        self.process_text_url = urljoin(self.base_url, "processQuantityText")
        self.parse_measures_url = urljoin(self.base_url, "parseMeasure")

    def process_pdf(self, file):

        files = {
            'input': (
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
            logger.debug('Quantities PDF extraction failed with error ' + str(status))
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

    def _test_server_connection(self, base_url):
        """Test if the server is up and running."""
        the_url = urljoin(base_url, "isalive")
        try:
            r = requests.get(the_url)
        except:
            logger.error("Grobid-quantities server does not appear up and running, the connection to the server failed")
            raise ServerUnavailableException

        status = r.status_code

        if status != 200:
            logger.info("Grobid-quantities server is running but connection failed with error code " + str(status))
            raise ServerUnavailableException
        else:
            logger.info("Grobid-quantities server is up and running")

    def _load_config(self, path="./config.json"):
        """
        Load the json configuration
        """
        config_json = open(path).read()
        return json.loads(config_json)

class QuantitiesClient:

    def __init__(self, base_url,
                 sleep_time=5,
                 timeout=60,
                 config_path=None,
                 check_server=True):

        self.client = QuantitiesAPI(base_url=base_url,
                                    sleep_time=sleep_time,
                                    timeout=timeout,
                                    config_path=config_path,
                                    check_server=check_server)

    def _process_file(self, file, output):
        logger.info("Processing " + file)
        response_code, result = self.client.process_pdf(file)

        if response_code == 503:
            logger.warning("Got 503, sleeping and retrying")
            time.sleep(5)
            return self._process_file(file, output)
        elif response_code == 200:
            pages = len(result['pages'])
            runtime = result['runtime'] / 1000
            pages_seconds = pages / runtime

            logger.info("Processed {} ({} pages) with runtime {} s. {} pages/second."
                        .format(file,
                                pages,
                                runtime,
                                pages_seconds))

            pdf_file_name = ntpath.basename(file)
            filename = join(output, splitext(pdf_file_name)[0] + '.json')
            try:
                with open(filename, 'w', encoding='utf8') as f:
                    json.dump(result, f)
            except BaseException as e:
                logger.error("Error when writing ", e)


        else:
            logger.error("Got error " + response_code + "from file :" + file + ". Skipping output. ")

    def _process_batch(self, batch, output_dir, n):
        print(len(batch), "PDF files to process")
        # with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        with ThreadPoolExecutor(max_workers=n) as executor:
            for file in batch:
                executor.submit(self._process_file, file, output_dir)

    def process(self, input_path, output_path, num_processes, force=False):
        logger.info("Processing data from {} using {} threads".format(input_path, num_processes))

        onlyfiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(input_path) for f in fn if
                     f.lower().endswith("pdf") and isfile(join(dp, f))]

        pdf_files = []

        for pdf_file in onlyfiles:
            pdf_files.append(pdf_file)

            if len(pdf_files) == num_processes:
                self._process_batch(pdf_files, output_path, num_processes)
                pdf_files = []

        # last batch
        if len(pdf_files) > 0:
            self._process_batch(pdf_files, output_path, num_processes)


def main():
    parser = argparse.ArgumentParser(description="Client for the Grobid-quantities service")
    parser.add_argument(
        "--input", default=None, required=True,
        help="path to the directory containing PDF files or .txt (for processCitationList only, "
             "one reference per line) to process"
    )
    parser.add_argument(
        "--output",
        required=False,
        default=None,
        help="path to the directory where to put the results (optional)",
    )
    parser.add_argument(
        "--base-url",
        required=False,
        default="http://localhost:8060/service",
        help="Base url of the service",
    )
    # parser.add_argument(
    #     "--config",
    #     default="./config.json",
    #     help="path to the config file, default is ./config.json",
    # )
    parser.add_argument("--n", default=10, help="concurrency for service usage")
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="force re-processing pdf input files when tei output files already exist",
    )
    # parser.add_argument(
    #     "--verbose",
    #     default=False,
    #     action="store_true",
    #     help="print information about processed files in the console",
    # )

    args = parser.parse_args()

    input_path = args.input
    # config_path = args.config
    output_path = args.output
    base_url = args.base_url

    if args.n is not None:
        try:
            n = int(args.n)
        except ValueError:
            print("Invalid concurrency parameter n:", n, ", n = 10 will be used by default")
            n = 10

    # if output path does not exist, we create it
    if output_path is not None and not os.path.isdir(output_path):
        try:
            print("output directory does not exist but will be created:", output_path)
            os.makedirs(output_path)
        except OSError:
            print("Creation of the directory", output_path, "failed")
        else:
            print("Successfully created the directory", output_path)

    force = args.force
    # verbose = args.verbose

    try:
        client = QuantitiesClient(base_url=base_url)
    except ServerUnavailableException:
        exit(-1)

    start_time = datetime.now()

    client.process(input_path, output_path, n, force)

    runtime = datetime.now() - start_time
    print("runtime: %s seconds " % (runtime.seconds))


if __name__ == "__main__":
    main()
