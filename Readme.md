#Useful resources

https://developer.box.com/reference#get-shared-link
https://github.com/box/box-python-sdk
https://developer.box.com/v2.0/docs/app-users
http://box-python-sdk.readthedocs.io/en/latest/
https://developer.box.com/docs/folder-structure
https://developer.box.com/v2.0/docs/get-all-users

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

