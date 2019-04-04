import sys
import time

from grobid.quantities_batch import QuantitiesBatch

if len(sys.argv) != 4:
    sys.exit("Missing parameter. Usage: python batch_sample.py /input/directory /output/directory nbThreads")

inputPath = sys.argv[1]
outputPath = sys.argv[2]
nbThreads = sys.argv[3]

#
# def saveFile(filename, result):
#     output = join(outputPath, os.path.basename(filename)) + ".json"
#     with open(output, 'w') as outfile:
#         json.dump(result, outfile)
#
#     print("Writing output to " + output)
#     return


start = time.time()
QuantitiesBatch('http://localhost:8060/service/').process(inputPath, outputPath, int(nbThreads))

print("Batch processed in " + str(time.time() - start))
