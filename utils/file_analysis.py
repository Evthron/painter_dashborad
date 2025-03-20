import os
import glob
from typing import (List, Dict, Optional)
from pathlib import Path

def get_latest_file(path : Path) -> Path :
    files = glob.glob(os.path.join(path, '*'))
    files.sort(key=os.path.getmtime, reverse=True)
    latest_file = files[0]
    return Path(latest_file)


def count_dirs(folders: List[Path],
               ignored_dirs : Optional[List[str]] = None) -> int:
    '''
    Recursively count a files paths in a list of folders
    >>> home = os.environ.get('HOME')
    >>> folders = [ home + "/Code/Python/custom_module/testdoc/book 7/"]
    >>> ignored_dirs = ["New Folder"]
    >>> count_dirs(folders, ignored_dirs) == 2
    True
    '''
    dir_count = 0
    for folder_path in folders:
        for _, dirs, _ in os.walk(folder_path):
            if ignored_dirs:
                dirs[:] = [dir_ for dir_ in dirs if dir_ not in ignored_dirs]
            dir_count += len(dirs)
    return dir_count

def count_files(folders: List[Path],
                ignored_dirs : Optional[List[str]] = None,
                ignored_files : Optional[List[str]] = None) -> int:
    '''
    Recursively count a files paths in a list of folders
    >>> home = os.environ.get('HOME')
    >>> folders = [ home + "/Code/Python/custom_module/testdoc/book 7/yes"]
    >>> ignored_files = ["20240311_033428 -- outdoors sight.jpg"]
    >>> count_files(folders, ignored_files=ignored_files) == 2
    True
    '''
    file_count = 0
    for folder_path in folders:
        for _, dirs, files in os.walk(folder_path):
            if ignored_dirs:
                dirs[:] = [dir_ for dir_ in dirs if dir_ not in ignored_dirs] 
            if ignored_files:
                files[:] = [file for file in files if file not in ignored_files]
            file_count += len(files)
    return file_count
            
def get_file_paths(folders : List[Path],
                  ignored_dirs : Optional[List[str]] = None,
                  ignored_files : Optional[List[str]] = None) -> List[Path]:
    '''
    Recursively get a list of file paths in a list of folders
    >>> home = os.environ.get('HOME')
    >>> folders = [ home + "/Code/Python/custom_module/testdoc/book 7"]
    >>> ignored_dir = ["ignore"]
    >>> file_list = get_file_paths(folders, ignored_dir)
    >>> len(file_list) == 3
    True
    >>> ignored_dir = None
    >>> file_list = get_file_paths(folders, ignored_dir)
    >>> len(file_list) == 36
    True
    >>> ignored_files = ["20240322_202310 -- outdoors copies.jpg"]
    >>> file_list = get_file_paths(folders, ignored_dir, ignored_files)
    >>> len(file_list) == 35
    True
    >>> type(file_list)
    <class 'list'>
    '''
    file_paths = []
    for folder_path in folders:
        for root, dirs, files in os.walk(folder_path):
            if ignored_dirs:
                dirs[:] = [dir_ for dir_ in dirs if dir_ not in ignored_dirs] 
            if ignored_files:
                files[:] = [file for file in files if file not in ignored_files]
            file_paths.extend([Path(root) / Path(file) for file in files])
    return file_paths

if __name__ == '__main__':
    import doctest
    doctest.testmod()