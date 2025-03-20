from typing import (List, Dict, Optional)
from pathlib import Path
import file_analysis
import os

def get_tag_list(file_name) -> List[str]:
    ''' Get the tags of the file stored in a list.'''
    if ' -- ' not in file_name:
        return []
    file_name = file_name.split(sep=' -- ')[1]
    file_name = file_name.split(sep='.')[0]
    file_tag_list = file_name.split(sep=' ')
    return file_tag_list


def has_tags(file_name, match_tag_list : List[str]) -> bool:
    '''
    check whether a filename string contains a certain tag
    '''
    tag_list = get_tag_list(file_name)
    for tag in match_tag_list:
        if tag not in tag_list:
            return False
    return True


def get_tag_filename_dict(filetags_path : Path,
                 folders : List[Path],
                 tag_label : Optional[List[str]] = None,
                 ignored_dirs : Optional[List[str]] = None,
                 ignored_files : Optional[List[str]] = None) -> Dict[str, int]:
    '''
    Generate a dictionary whose keys are the tags specified by tag_types.
    tag_types is the comment after the tag in .filetag, e.g. tag1 #type1
    The value of the dictionary is a list containing all the filename string associated with the tags.
    if no tag_types is given, use all the tags.
    '''
    tag_dict = dict()
    # required to initiate dir_count and file_count as None to correctly order them on the top
    tag_dict['dir_count'] = None
    tag_dict['file_count'] = None
    fin = open(filetags_path, encoding='utf-8')
    for line in fin:
        line = line.strip()
        if tag_label is None:
            tag = line.split(sep=' ')[0]
            tag_dict[tag] = []
        else:
            for tag_type in tag_label:
                if tag_type in line:
                    tag = line.split(sep=' ')[0]
                    tag_dict[tag] = []

    '''
    Count the number of files and dirs in the specified path
    '''
    files : List[Path] = file_analysis.get_file_paths(folders, ignored_dirs, ignored_files)
    tagged_file_names : List[str] = [path.name for path in files if ' -- ' in path.name]
    tag_dict['dir_count'] = file_analysis.count_dirs(folders, ignored_dirs)
    tag_dict['file_count'] = [] # Only count the files that have the specified tags
    
    ''' For each tag, find the filenames contain the tag and append them to the tag dictionary'''
    for file_name in tagged_file_names:
        file_tag_list = get_tag_list(file_name)
        have_tag = False
        for tag in tag_dict.keys():
            if tag in file_tag_list:
                tag_dict[tag].append(file_name)
                have_tag = True
        if have_tag: # if the file has tag, add its filename to file_count
            tag_dict['file_count'].append(file_name)
    return tag_dict

        
def get_tag_count_dict(filetags_path : Path,
                             folders : List[Path],
                             tag_label : Optional[List[str]] = None,
                             ignored_dirs : Optional[List[str]] = None,
                             ignored_files : Optional[List[str]] = None) -> Dict[str, int]:
    '''
    Tally the files
    >>> home = os.environ.get('HOME')
    >>> filetags_path = home + "/Code/Python/custom_module/testdoc/.filetags"
    >>> folders = [home + "/Code/Python/custom_module/testdoc/book 7"]
    >>> tag_label = ["skill"]
    >>> ignored_dir = ["ignore"]
    >>> skill_stats = get_tag_count_dict(filetags_path, folders, tag_label, ignored_dir)
    >>> skill_stats["dir_count"] == 3
    True
    >>> skill_stats["file_count"] == 1
    True
    >>> skill_stats["figures"] == 1
    True
    >>> ignored_dir = None
    >>> skill_stats = get_tag_count_dict(filetags_path, folders, tag_label, ignored_dir)
    >>> skill_stats["dir_count"] == 4
    True
    '''
    tag_dict = get_tag_filename_dict(filetags_path, folders, tag_label, ignored_dirs, ignored_files)
    
    ''' Count the number of filenames under each tag and tally them'''
    for key, value in tag_dict.items():
        if key != 'dir_count':
            tag_dict[key] = len(value)
            
    return tag_dict
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()