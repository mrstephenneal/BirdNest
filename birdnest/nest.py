# Nest related files into sub-folders
import os
import shutil
from dirutility import DirPaths, ZipBackup
from tqdm import tqdm
from PySimpleGUI import PySimpleGUI as sg


class Nest:
    def __init__(self, root, separator='_', limit=1, file_types=None, zip_backup=False):
        """
        :param root: Root directory of to-be nested files
        :param separator: Character separating meaningful file name segments
        :param file_types:
        """
        self._root = root
        self._file_types = file_types
        self.separator = separator
        self._limit = limit

        # Create a zip backup to revert back to
        if zip_backup:
            ZipBackup(root, overwrite=False).backup()

        # New directories to create
        self.new_dirs = set([])

    def _abs_path(self, relative):
        """
        Retrieve an absolute path by join root and a relative file path.

        :param relative: File path within the root directory
        :return: absolute file path
        """
        return os.path.join(self._root, relative)

    def _create_directory(self, directory):
        """Create a directory if it does not exist."""
        directory_path = self._abs_path(directory)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def parse_directory(self):
        """
        Scan the directory for file's eligible to-be nested.

        Only accept files that contain the 'separator' character and match file_type filters.
        """
        return [fp for fp in DirPaths(self._root, True, to_include=self._file_types, max_level=1).walk()
                if self.separator in fp]

    def map_results(self):
        """Create dictionary of sources and destinations by analyzing the files found by parse_directory()."""
        nest = {}
        for file_path in self.parse_directory():
            # Get file_name only
            basename = os.path.basename(file_path)

            # Get destination directory by splitting on separator and add to new_dirs
            dst_directory = basename.split(self.separator, 1)[0]
            self._create_directory(dst_directory)

            # Add file_path and destination to nest dictionary
            nest[file_path] = dst_directory
        return nest

    def nest(self):
        """Move files from their original source destination to their new directory."""
        # Move files
        nest = self.map_results().items()
        for file_path, directory in tqdm(nest, 'Moving files to destination folders', len(nest)):
            shutil.move(str(file_path), self._abs_path(os.path.join(directory, os.path.basename(file_path))))


def main():
    root = sg.PopupGetFolder('Select a root directory')
    Nest(root, zip_backup=True).nest()


if __name__ == '__main__':
    main()
