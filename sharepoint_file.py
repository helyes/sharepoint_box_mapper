"""
 Represents a file on sharepoint
"""
from urllib.parse import (unquote_plus)

class SharepointFile:
    """Sharepoint file"""

    file = None

    def __init__(self, file):
        self.file = file
        self.file_id = file['id']
        

    def get_filename(self):
        """Returns human filename"""
        return unquote_plus(self.file['name'])

    def get_full_path(self):
        """Returns full path includign filename"""        
        return self.file['path']


    # def get_folder(self):
    #     """Returns full containing path of the file"""
    #     mylist = self.shared_item.path_collection

    #     # for key, value in mylist.items():
    #     #     print (key, value)

    #     #print('Total count: ' , mylist['total_count'])
    #     #print('Folder: ' , mylist['entries'][1])
    #     path = '/'
    #     for folder in mylist['entries']:
    #         # print(x['name'])
    #         path = path + folder['name'] + '/'
    #     return path


    # def get_type(self):
    #     """Returns shared link type: folder or file"""
    #     return self.shared_item_type
