"""
 Small helper functions for file operations
"""
import os
from pathlib import Path

class FileHelper:
    """Utility functions for file operations"""

    @staticmethod
    def get_output_file_path(input_file_path, first, limit):
        """Returns the output file pathe based on input_file_path, first and limit parameters\n
        Example:
          Input file: input.csv
          First: 10
          Limit: 99
        Generated output filename:
          input-result-10-109.csv
        """
        (filepath, filename) = os.path.split(input_file_path)
        (basename, extension) = os.path.splitext(filename)
        ret_basename = basename + '-result'
        ret_basename = ret_basename + '-' + format(first, '05')
        ret_basename = ret_basename + '-' + str(('end' if limit == 0 else format(first+limit, '05')))
        return os.path.join(filepath, (ret_basename + extension))

    @staticmethod
    def remove_file(thepath):
        """Silently removes given file"""
        try:
            my_file = Path(thepath)
            if my_file.is_file():
                print('Removing', thepath)
            os.remove(thepath)
        except OSError:
            pass
