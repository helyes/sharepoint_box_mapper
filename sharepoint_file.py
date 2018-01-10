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
