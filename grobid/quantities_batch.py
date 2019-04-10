import io
import json
import ntpath
import os
import sys
import time
from concurrent.futures.process import ProcessPoolExecutor
from os import listdir
from os.path import isfile, join, splitext

from zenlog import logging

from grobid.quantities import QuantitiesClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '\n\n %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
stream.setFormatter(formatter)
logger.addHandler(stream)


class QuantitiesBatch:

    def __init__(self, apiBase=None):
        if apiBase:
            self.client = QuantitiesClient(apiBase=apiBase)
        else:
            self.client = QuantitiesClient()

    def process_file(self, file, output):
        logger.info("Processing " + file)
        response_code, result = self.client.process_pdf(file)

        if response_code == 503:
            logger.warning("Got 503, sleeping and retrying")
            time.sleep(5)
            return self.process_file(file, output)
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

    def process_batch(self, batch, output_dir, n):
        print(len(batch), "PDF files to process")
        # with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        with ProcessPoolExecutor(max_workers=n) as executor:
            for file in batch:
                executor.submit(self.process_file, file, output_dir)

    def process(self, input_path, output_path, num_processes):
        logger.info("Processing data from {} using {} threads".format(input_path, num_processes))

        onlyfiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(input_path) for f in fn if
                     f.lower().endswith("pdf") and isfile(join(dp, f))]

        pdf_files = []

        for pdf_file in onlyfiles:
            pdf_files.append(pdf_file)

            if len(pdf_files) == num_processes:
                self.process_batch(pdf_files, output_path, num_processes)
                pdf_files = []

        # last batch
        if len(pdf_files) > 0:
            self.process_batch(pdf_files, output_path, num_processes)
