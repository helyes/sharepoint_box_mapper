# Sharepoint/box share link generator

Loads CSV file including either box share links or sharepoint file locations and generetas the correspondign sharepoint view url.

## Requirements

* Python3
* Configured Azure app (app id and app secret)
* Configured Box app (token)

## Limitations

Only *view* links can be generated as embed links are limited to personal onedrive accounts

#Useful resources

## Sharepoint

[Azure graph explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)

[Getting azure tenant id](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Properties)

Microsoft calls both tenant id or directory id.

[Get azure token](https://developer.microsoft.com/en-us/graph/docs/concepts/auth_v2_service)

    POST https://login.microsoftonline.com/{azure-tenant-id}/oauth2/v2.0/token
        Content-Type: application/x-www-form-urlencoded
        
        grant_type=client_credentials
        client_id={id}
        client_secret={secret}
        scope=https%3A%2F%2Fgraph.microsoft.com%2F.default

[Get a DriveItem resource](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_get)
    
    GET /drives/{drive-id}/root:/{path}
    authorization: Bearer {token}

[Share an item](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_createlink)

    POST /{drive-id}/drive/items/{item-id}/createLink
    Content-Type: application/json
    authorization: Bearer {token}

        {
         "type": "view",
         "scope": "anonymous"
        }


## Sharepoint command parameters

    $ ./sharepoint_file_loader.py -h
    Starting...
    usage: sharepoint_file_loader.py [-h] [-i] [-f] [-l] [-b] [-s] [-r] [-p] [-o]
                                    [-a] [-v]

    Adds and populates sharepoint share url-s based on file location

    Required arguments:
    -i , --input          The input file to parse
    -f , --first          Start point. If -f 20 and -l 11, entries from row 20
                            to 30 will be processed
    -l , --limit          Number of entries to process
    -b , --sharepointlocationcolumn 
                            Column name in csv that contains the location of the
                            file
    -s , --spclientsecret 
                            Sharepoint client secret key. Format:
                            Jwt12345678901234567890/1234567890123456789=
    -r , --sproot         Sharepoint root folder
    -p , --spclientid     Sharepoint client id. Format:
                            12345678-1234-1234-1234-123456789012
    -o , --onedriveid     Onedrive id. Format: b!xx-sdasdfasdfasdfasdfasdfsada--
                            asdasdfasdf
    -a , --azuretenantid 
                            Azure tenant id. Format:
                            12345678-1234-45d7-1234-123456789012

    Optional arguments:
    -v, --verbose         Verbose logging

    Output file will be {input}-result.csv


## Box

[App page to get developer token](https://app.box.com/developers/console/app/{app_id}/configuration)

[API reference and playground](https://developer.box.com/reference)

## Box command parameters

    $ ./box_file_loader.py -h
    Starting...
    usage: box_file_loader.py [-h] [-i] [-f] [-l] [-t] [-b] [-s] [-p] [-o] [-a]
                            [-v]

    Adds and populates file location and share type (folder/file) column to a csv
    including box shared url-s

    Required arguments:
    -i , --input          The input file to parse
    -f , --first          Start point. If -f 20 and -l 11, entries from row 20
                            to 30 will be processed
    -l , --limit          Number of entries to process
    -t , --token          Box developer token generated on Box app page (https:/
                            /app.box.com/developers/console/app/123456/configurati
                            on page
    -b , --boxurlcolumn   Column name in csv that contains the box shared url
    -s , --spclientsecret 
                            Sharepoint client secret key. Format:
                            Jwt12345678901234567890/1234567890123456789=
    -p , --spclientid     Sharepoint client id. Format:
                            12345678-1234-1234-1234-123456789012
    -o , --onedriveid     Onedrive id. Format: b!xx-sdasdfasdfasdfasdfasdfsada--
                            asdasdfasdf
    -a , --azuretenantid 
                            Azure tenant id. Format:
                            12345678-1234-45d7-1234-123456789012

    Optional arguments:
    -v, --verbose         Verbose logging

    Output file will be {input}-result.csv


## ETC

https://developer.box.com/reference#get-shared-link

https://github.com/box/box-python-sdk

https://developer.box.com/v2.0/docs/app-users

https://developer.box.com/docs/folder-structure

https://developer.box.com/v2.0/docs/get-all-users

# Processing files with sharepoint location

    ./sharepoint_file_loader.py -p {client id} -s {client secret} -o {onedrive id} -a {azure tenant id} -r {sharepoint root folder}  -i ./import.csv -b file_path -f 1 -l 500

Input (input.csv)

    foo,bar,file_path
    foo1,bar1,/folder/subfolder/doc.pdf
    foo2,bar2,/anotherfolder/subfolder/doc2.pdf
    foo3,bar4,/anotherfolder/subfolder/doc3.pdf

Output (input-result.csv)

    foo,bar,file_path,sharepoint
    foo1,bar1,/folder/subfolder/doc.pdf,https://company.sharepoint.com/sites/main/_layouts/15/guestaccess.aspx?docid=123123123123123123&authkey=1231231231231
    foo2,bar2,/anotherfolder/subfolder/doc2.pdf,https://company.sharepoint.com/sites/main/_layouts/15/guestaccess.aspx?docid=223123123123123124&authkey=1231231231230
    foo3,bar3,/anotherfolder/subfolder/doc3.pdf,ERROR: File {sharepoint root folder} /anotherfolder/subfolder/doc3.pdf does not exist


### Generating new import files including errors only

Running the below one liner will filter out the ERROR records from a previous run and creates a file with identical layout as the original input file. The gerated file includes failed entries only thus it can be used again for reprocessing.

This is a template, pay attention to awk parameters as they depend on csv structure. The below prints column 1 to 5.

The file will *NOT* contain the header lines. Need to be added manually.

    cat 6-os2-db-tables-having-box-links-prod-copy-result-fixed-quoted.csv | awk -F "," '/ERROR/ {print $1","$2","$3","$4","$5}'  > 6-errors-$(date "+%Y-%m-%d-%H-%M-%S").csv

*Original csv file including box links*
    
    Table,Field1,Field2,Field3,Link
    field_data_field_topic_section_body,entity_id,field_topic_section_body_value,34119,https://app.box.com/shared/aerfadfasdfaefawrefaewrf/1/123123131123/1231231231/1
    field_revision_field_topic_section_body,revision_id,field_topic_section_body_value,34124,https://app.box.com/shared/sdrfgsergaserfserfaef/1/12345678901/1231231231/1

*First output file, includign error records*
    
    Table,Field1,Field2,Field3,Link,location_type,location,sharepoint
    field_data_field_topic_section_body,entity_id,field_topic_section_body_value,34119,https://app.box.com/shared/aerfadfasdfaefawrefaewrf/1/123123131123/1231231231/1,folder,/Files/Example/,https://mycompany.sharepoint.com/sites/main/_layouts/15/guestaccess.aspx?docid=awefargaer23radsfasdfa&authkey=123124asdfadf
    field_revision_field_topic_section_body,revision_id,field_topic_section_body_value,34124,https://app.box.com/shared/sdrfgsergaserfserfaef/1/12345678901/1231231231/1,UKNOWN,N/A,ERROR: Box location uknown

*One liner output*
    
    Table,Field1,Field2,Field3,Link
    field_revision_field_topic_section_body,revision_id,field_topic_section_body_value,34124,https://app.box.com/shared/sdrfgsergaserfserfaef/1/12345678901/1231231231/1

