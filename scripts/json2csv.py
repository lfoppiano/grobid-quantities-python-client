# This script converts the json files from the quantitites API to a CSV that can be used to be indexed
import csv
import json
import os
import sys
import uuid
from os.path import isfile, join


def quantity2List(quantity):
    outputList = []

    # Raw Value
    rawValue = quantity.get('rawValue')
    rawValue = rawValue.replace('\n', '')
    outputList.append(rawValue)

    # Raw Unit
    rawUnit = quantity.get('rawUnit')
    if not 'rawUnit' in quantity:
        outputList.append("")
        outputList.append("")
        outputList.append("")
    else:
        rawUnitValue = rawUnit.get('name')
        rawUnitValue = rawUnitValue.replace('\n', '')
        outputList.append(rawUnitValue.strip())
        outputList.append(rawUnit.get('type'))
        outputList.append(rawUnit.get('system'))

    parsedValue = quantity.get('parsedValue')
    if not parsedValue:
        outputList.append("")
        outputList.append("")
    else:
        outputList.append(parsedValue.get('numeric'))

    normalisedQuantity = quantity.get('normalizedQuantity')

    if not normalisedQuantity:
        outputList.append("")
    else:
        outputList.append(normalisedQuantity)

    normalisedUnit = quantity.get('normalizedUnit')

    if not normalisedUnit:
        outputList.append("")
        outputList.append("")
        outputList.append("")
    else:
        outputList.append(normalisedUnit.get('name'))
        outputList.append(normalisedUnit.get('type'))
        outputList.append(normalisedUnit.get('system'))

    return outputList


def interval2csv(measurement):
    outputList = []

    id = uuid.uuid4()

    quantityLeast = measurement.get('quantityLeast')
    quantityLeastList = []
    if quantityLeast:
        quantityLeastList.append(id)
        quantityLeastList.append('>')
        quantityLeastList.extend(quantity2List(quantityLeast))
        outputList.append(quantityLeastList)
        quantified_object = measurement.get('quantified')
        if not quantified_object:
            quantityLeastList.append("")
            quantityLeastList.append("")
        else:
            quantityLeastList.append(quantified_object['rawName'])
            quantityLeastList.append(quantified_object['normalizedName'])

    quantityMost = measurement.get('quantityMost')
    quantityMostList = []
    if quantityMost:
        quantityMostList.append(id)
        quantityMostList.append('<')
        quantityMostList.extend(quantity2List(quantityMost))
        outputList.append(quantityMostList)
        quantified_object = measurement.get('quantified')
        if not quantified_object:
            quantityMostList.append("")
            quantityMostList.append("")
        else:
            quantityMostList.append(quantified_object['rawName'])
            quantityMostList.append(quantified_object['normalizedName'])

    return outputList


def value2csv(measurement):
    outputList = []

    id = uuid.uuid4()

    quantity = measurement.get('quantity')

    outputList.append(id)
    outputList.append('=')
    outputList.extend(quantity2List(quantity))

    quantified_object = measurement.get('quantified')
    if not quantified_object:
        outputList.append("")
        outputList.append("")
    else:
        outputList.append(quantified_object['rawName'])
        outputList.append(quantified_object['normalizedName'])

    return [outputList]


def list2csv(measurement):
    outputList = []

    id = uuid.uuid4()

    quantityList = measurement.get('quantities')

    for quantity in quantityList:
        quantityListOutput = []
        quantityListOutput.append(id)
        quantityListOutput.append('l')
        quantityListOutput.extend(quantity2List(quantity))

        quantified_object = measurement.get('quantified')
        if not quantified_object:
            quantityListOutput.append("")
            quantityListOutput.append("")
        else:
            quantityListOutput.append(quantified_object['rawName'])
            quantityListOutput.append(quantified_object['normalizedName'])
        outputList.append(quantityListOutput);

    return outputList


processMap = {
    'value': value2csv,
    'interval': interval2csv,
    'listc': list2csv
}


def process(files, output_file):
    with open(output_file, mode='w') as output:
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        for file in files:
            with open(file, 'r') as f:
                loaded = json.load(f)

                if 'measurements' not in loaded:
                    break

            for measurement in loaded['measurements']:
                row_list = processMap.get(measurement.get('type'))(measurement)
                if row_list:
                    for subList in row_list:
                        writer.writerow(subList)


if len(sys.argv) != 3:
    sys.exit("Missing parameter. Usage: python json2csv.py /input/directory output_file")

inputPath = sys.argv[1]
outputFile = sys.argv[2]

only_files = [os.path.join(dp, f) for dp, dn, fn in os.walk(inputPath) for f in fn if
              f.lower().endswith("json") and isfile(join(dp, f))]

print("Processing " + str(len(only_files)) + " files.")

process(only_files, outputFile)
