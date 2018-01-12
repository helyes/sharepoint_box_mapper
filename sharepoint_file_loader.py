#!/usr/bin/env python3
import csv
import argparse
from pprint import pprint
from time import sleep
import time

from file_helper import FileHelper
from print_color import PrintColor
from sharepoint_client import SharepointClient

COLORS = {
    'header' : PrintColor.HEADER,
    'file' : PrintColor.OKGREEN,
    'folder' : PrintColor.WARNING,
    'UNKNOWN' : PrintColor.FAIL,
}

print(COLORS['header'] + 'Starting...' + PrintColor.ENDC)

parser = argparse.ArgumentParser(
    description='Adds and populates sharepoint share url-s based on file location',
    epilog='Output file will be {input}-result.csv'
    )
parser._action_groups.pop()
required = parser.add_argument_group('Required arguments')
required.add_argument("-i", "--input", metavar='', type=str, default="input.csv",
                      help="The input file to parse")
required.add_argument("-f", "--first", metavar='', type=int, default=0,
                      help="Start point. If -f 20 and -l 11, entries from row 20 to 30 will be processed")
required.add_argument("-l", "--limit", metavar='', type=int, default=0,
                      help="Number of entries to process")
required.add_argument("-b", "--sharepointlocationcolumn", metavar='', type=str,
                      help="Column name in csv that contains the location of the file")
required.add_argument("-s", "--spclientsecret", metavar='', type=str,
                      help="Sharepoint client secret key. Format: Jwt12345678901234567890/1234567890123456789=")
required.add_argument("-r", "--sproot", metavar='', type=str,
                      help="Sharepoint root folder")
required.add_argument("-p", "--spclientid", metavar='', type=str,
                      help="Sharepoint client id. Format: 12345678-1234-1234-1234-123456789012")
required.add_argument("-o", "--onedriveid", metavar='', type=str,
                      help="Onedrive id. Format: b!xx-sdasdfasdfasdfasdfasdfsada--asdasdfasdf")
required.add_argument("-a", "--azuretenantid", metavar='', type=str,
                      help="Azure tenant id. Format: 12345678-1234-45d7-1234-123456789012")



optional = parser.add_argument_group('Optional arguments')
optional.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

args = parser.parse_args()

SHAREPOINT_LOCATION_COLUMN_NAME = args.sharepointlocationcolumn

print('Input file:\t', args.input)
print('Sharepoint location column:\t', SHAREPOINT_LOCATION_COLUMN_NAME + ', Starting at position', args.first, 'and loading', ('all' if args.limit == 0 else args.limit), 'entries')
OUTPUT_FILE = FileHelper.get_output_file_path(input_file_path=args.input, first=args.first, limit=args.limit)
print('Output file:\t', OUTPUT_FILE)
sharepoint_client = SharepointClient(client_id=args.spclientid, client_secret=args.spclientsecret, onedrive_id=args.onedriveid, azure_tenant_id=args.azuretenantid)
#sys.exit()

FileHelper.remove_file(OUTPUT_FILE)

CSV_IN = open(args.input, newline='')

#calculate rowcount
CSV_IN_ROW_COUNT = sum(1 for row in CSV_IN)
print('Input row count:', CSV_IN_ROW_COUNT)
print('Starting from entry:', args.first, ' - Excluding header')
CSV_IN.seek(0)
LAST_ENTRY = CSV_IN_ROW_COUNT if args.limit == 0 else args.first + args.limit-1
LIMIT = LAST_ENTRY - args.first +1
#print('LIMIT:', LIMIT, 'LAST_ENTRY:', LAST_ENTRY)
# Reading inpout and writing output in the same loop
#with open(args.input, newline='') as csvfile:
#READER = csv.DictReader(CSV_IN, fieldnames=input_field_names)
READER = csv.DictReader(CSV_IN)

input_field_names = READER.fieldnames

#Setting up output writer
CSV_OUT = open(OUTPUT_FILE, 'w', newline='')

output_field_names = input_field_names + ['sharepoint']
WRITER = csv.DictWriter(CSV_OUT, fieldnames=output_field_names)
WRITER.writeheader()

error_count_sharepoint = 0
print('Input fields: ' + ', '.join(input_field_names))
counter = 0

for row in READER:
    counter += 1
    if args.first > 1 and counter == 1:
        print('Seeking to entry', args.first)
    if counter < args.first:
        #print ('Skipping row', counter, row[SHAREPOINT_LOCATION_COLUMN_NAME])
        continue

    print(COLORS['header'] + \
        '[' + str(counter-args.first+1) + '/' + str(LIMIT-1) +'/'  + str(CSV_IN_ROW_COUNT-1) + '] ' + \
        'Processing ', row[SHAREPOINT_LOCATION_COLUMN_NAME] + PrintColor.ENDC)

    start_time = time.time()

    #sharepoint
    try:
        f = sharepoint_client.get_sharepoint_file(args.sproot+row[SHAREPOINT_LOCATION_COLUMN_NAME])
        print('  Sharepoint:\t' + PrintColor.OKGREEN + f.get_full_path() + PrintColor.ENDC, 'Id:', f.file_id)
        public_url = sharepoint_client.get_shared_url_public(f)
        row.update({'sharepoint' : public_url})
        print('  Share url:  ', PrintColor.OKGREEN, row['sharepoint'], PrintColor.ENDC)
    except Exception as error:
        #print (error)
        error_count_sharepoint = error_count_sharepoint + 1
        row.update({'sharepoint' : 'ERROR: ' + error.args[0]})
        print('  Sharepoint: ', PrintColor.FAIL, error.args[0], PrintColor.ENDC)


    WRITER.writerow(row)
    if counter % 2 == 0:
        CSV_OUT.flush()
    if counter == LAST_ENTRY:
        break

    #limit calls, max 10 per second. This is VERY unlikely to happen, hence the hardcoded sleep time
    if (time.time() - start_time) < 0.1:
        sleep(0.1)

CSV_OUT.close()
CSV_IN.close()

print('\n\nFile', args.input, 'has been successfully processed.')
print('Number of processed entries:', str(CSV_IN_ROW_COUNT-args.first) + ', Errors:', str(error_count_sharepoint))
