import json
import pkg_resources


def wanikani_subjects_indexed():
    file_path = pkg_resources.resource_filename(__name__, 'wanikani/wanikani_subjects_indexed.json')
    with open(file_path, 'rt', encoding='utf-8') as fp:
        return json.load(fp)


def character_images_dir():
    if pkg_resources.resource_isdir(__name__, 'images'):
        return pkg_resources.resource_filename(__name__, 'images')
    else:
        raise EnvironmentError('Package is not set up properly. Images folder is missing or misnamed.')


def character_data_dir():
    if pkg_resources.resource_isdir(__name__, 'wanikani'):
        return pkg_resources.resource_filename(__name__, 'wanikani')
    else:
        raise EnvironmentError('Package is not set up properly. Missing character data folder "wanikani"')
