"""
 Represents a shared file on box
"""
from urllib.parse import (unquote_plus)
from pprint import pprint

class BoxFile:
    """Box shared file"""

    file_id = None
    shared_item_type = None

    def __init__(self, shared_item):
        #print('Initializing box file...')
        #print('shared_item: ', shared_item)
        self.shared_item = shared_item
        self.file_id = self.shared_item['id']
        self.shared_item_type = self.shared_item['type']
        #print('Box file initialized, Type:',self.shared_item_type +', Name:', self.get_filename())

    def get_filename(self):
        """Returns human filename. Box file name is url decoded, including + signs"""
        #return unquote_plus(self.shared_item['name'])
        return self.shared_item['name']

    def get_folder(self):
        """Returns full containing path of the file"""
        mylist = self.shared_item['path_collection']
        # for key, value in mylist.items():
        #     print (key, value)

        #print('Total count: ' , mylist['total_count'])
        #print('Folder: ' , mylist['entries'][1])
        path = '/'
        for folder in mylist['entries']:
            # print(x['name'])
            path = path + folder['name'] + '/'
        return path

    def get_full_path(self):
        """Returns full path includign filename"""
        folder = self.get_folder()
        filename = self.get_filename()
        return folder + filename

    def get_type(self):
        """Returns shared link type: folder or file"""
        return self.shared_item_type

