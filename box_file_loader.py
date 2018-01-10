#!/usr/bin/env python3
"""
 Parses csv files containing box shared url-s and appends a shared file location column to it
 Example input:

 Line,FileName,Link
 27798,page_590.html,https://app.box.com/s/12345678901234567890123456789012
 27799,page_728.html,https://app.box.com/s/12345678901234567890123456789012

 Example output:
 Line,FileName,Link,location_type,location,sharepoint
 27798,page_590.html,https://app.box.com/s/12345678901234567890123456789012,folder,/All Files/html,https://mycompany.sharepoint.com/sites/my_space/_layouts/15/guestaccess.aspx?folderid=21234123412341234512345213451213A&authkey=122121212-123131-HS-3Cw
 27799,page_728.html,https://app.box.com/s/12345678901234567890123456789012,folder,/All Files/html,https://mycompany.sharepoint.com/sites/my_space/_layouts/15/guestaccess.aspx?folderid=0a1d06a976a57498a807de0ecaf6fb1df&authkey=121212121-234232-HS-3Cw

"""

import csv, argparse
#from pprint import pprint
from time import sleep
import time

#https://github.com/box/box-python-sdk/blob/1.5/demo/example.py
from box_file import BoxFile
from box_client import BoxClient
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
    description='Adds and populates file location and share type (folder/file) column to a csv including box shared url-s',
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
required.add_argument("-t", "--token", metavar='', type=str,
                      help="Box developer token generated on Box app page (https://app.box.com/developers/console/app/123456/configuration page")
required.add_argument("-b", "--boxurlcolumn", metavar='', type=str,
                      help="Column name in csv that contains the box shared url")
required.add_argument("-s", "--spclientsecret", metavar='', type=str,
                      help="Sharepoint client secret key. Format: Jwt12345678901234567890/1234567890123456789=")
required.add_argument("-p", "--spclientid", metavar='', type=str,
                      help="Sharepoint client id. Format: 12345678-1234-1234-1234-123456789012")
required.add_argument("-o", "--onedriveid", metavar='', type=str,
                      help="Onedrive id. Format: b!xx-sdasdfasdfasdfasdfasdfsada--asdasdfasdf")
required.add_argument("-a", "--azuretenantid", metavar='', type=str,
                      help="Azure tenant id. Format: 12345678-1234-45d7-1234-123456789012")

optional = parser.add_argument_group('Optional arguments')
optional.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

args = parser.parse_args()

BOX_URL_COLUMN_NAME = args.boxurlcolumn

print('Input file:\t', args.input)
print('Box url column:\t', BOX_URL_COLUMN_NAME + ', Starting at position', args.first, 'and loading', ('all' if args.limit == 0 else args.limit), 'entries')
OUTPUT_FILE = FileHelper.get_output_file_path(input_file_path = args.input, first=args.first, limit=args.limit)
print('Output file:\t', OUTPUT_FILE)
box_client = BoxClient(token=args.token, debug=args.verbose)
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

#Reading inpout and writing output in the same loop
#with open(args.input, newline='') as csvfile:
#READER = csv.DictReader(CSV_IN, fieldnames=input_field_names)
READER = csv.DictReader(CSV_IN)

input_field_names = READER.fieldnames

#Setting up output writer
CSV_OUT = open(OUTPUT_FILE, 'w', newline='')

output_field_names = input_field_names + ['location_type', 'location', 'sharepoint']
WRITER = csv.DictWriter(CSV_OUT, fieldnames=output_field_names)
WRITER.writeheader()

error_count_box = 0
error_count_sharepoint = 0
print('Input fields: ' + ', '.join(input_field_names))
counter = 0
for row in READER:
    counter += 1
    if args.first > 1 and counter == 1:
        print('Seeking to entry', args.first)
    if counter < args.first:
        #print ('Skipping row', counter, row[BOX_URL_COLUMN_NAME])
        continue

    #omit commits
    if row[input_field_names[0]].startswith('#'):
        print(PrintColor.WARNING + 'Omitting entry [' + str(counter) + ']: ' + PrintColor.ENDC + row[input_field_names[0]] + '...')
        continue

    print(COLORS['header'] + \
        '[' + str(counter-args.first+1) + '/' + str(LIMIT-1) +'/'  + str(CSV_IN_ROW_COUNT-1) + '] ' + \
        'Processing ', row[BOX_URL_COLUMN_NAME] + PrintColor.ENDC)

    theFile = None
    start_time = time.time()

    try:
        sanitized_url = box_client.sanitize_shared_url(shared_url=row[BOX_URL_COLUMN_NAME])
        shared_item = box_client.get_shared_item(sanitized_url)
        theFile = BoxFile(shared_item)
        row.update({'location_type' :  theFile.get_type()})
        row.update({'location' : theFile.get_full_path()})
        print(PrintColor.OKBLUE, 'Done.' + PrintColor.ENDC, row[BOX_URL_COLUMN_NAME])
        print('  Box\t\t' + COLORS[row['location_type']] + row['location_type'].upper() + ':', row['location'] + PrintColor.ENDC)
    except Exception as error:
        #print('Error:', error.args[0])
        error_count_box += 1
        print(PrintColor.OKBLUE, 'Done.' + PrintColor.ENDC, row[BOX_URL_COLUMN_NAME])
        print('  Box\t\t' + PrintColor.FAIL + 'Could not find item:' + row[BOX_URL_COLUMN_NAME] + PrintColor.ENDC)
        row.update({'location_type' : 'UNKNOWN'})
        row.update({'location' : 'N/A'}) #careful, value used bow in if conditions

    #sharepoint
    try:
        if row['location'] == 'N/A':
            raise ValueError('Box location unkown')
        f = sharepoint_client.get_sharepoint_file(theFile.get_full_path().partition('All Files/')[2])
        print('  Sharepoint:\t' + PrintColor.OKGREEN + f.get_full_path() + PrintColor.ENDC, 'Id:', f.file_id)
        public_url = sharepoint_client.get_shared_url_public(f)
        #public_url = 'blah'
        row.update({'sharepoint' : public_url})
        print('  Share url:  ', PrintColor.OKGREEN, row['sharepoint'], PrintColor.ENDC)
    except Exception as error:
        #print (error)
        error_count_sharepoint = error_count_sharepoint + (0 if row['location'] == 'N/A' else 1)
        row.update({'sharepoint' : 'ERROR: ' + error.args[0]})
        print('  Sharepoint: ', PrintColor.FAIL, error.args[0], PrintColor.ENDC)


    WRITER.writerow(row)
    if counter % 2 == 0:
        CSV_OUT.flush()
    #print('Counter: ' , counter, 'first:', args.first, 'limit:', args.limit)
    if counter == LAST_ENTRY:
        break

    #box limits calls, max 10 per second. This is VERY unlikely to happen, hence the hardcoded sleep time
    if (time.time() - start_time) < 0.1:
        sleep(0.1)

CSV_OUT.close()
CSV_IN.close()

print('\n\nFile', args.input, 'has been successfully processed.')
print('Number of processed entries:', str(CSV_IN_ROW_COUNT-args.first) + ', Box errors:', str(error_count_box) + ', Sharepoint errors:', str(error_count_sharepoint))
