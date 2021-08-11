import json
import requests
import os

from wanikani_api.client import Client

from kanji_deck_creator.data.appdata import character_images_dir, character_data_dir


def _download_image(url: str, output_folder: str, name: str):
    last_slash = url.rfind('/')
    ext_start = url.find('.', last_slash)
    if '?' in url:
        ext_end = url.rfind('?')
        ext = url[ext_start:ext_end]
    else:
        ext = url[ext_start:]

    output_path = os.path.join(output_folder, name + ext)
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as fp:
        for chunk in response.iter_content(1024):
            fp.write(chunk)

    return name + ext


if __name__ == '__main__':
    images_folder = character_images_dir()
    character_data_folder = character_data_dir()
    subjects_indexed_file_path = os.path.join(character_data_folder, "wanikani_subjects_indexed.json")

    api_key = input("Input WaniKani api key: ").strip()
    client = Client(api_key)

    print("Fetching subjects from wanikani...")
    all_subjects = client.subjects(fetch_all=True)

    subject_list = []
    for subject in all_subjects:
        subject_list.append(subject._raw)

    indexed_json = {
        "character_lookup": {
            "radical": {},
            "kanji": {},
            "vocabulary": {}
        },
        "subjects": {
            subject["id"]: subject for subject in subject_list
        }
    }

    print("Indexing subjects and downloading images...")
    for subject in subject_list:
        indexed_json["subjects"][subject["id"]] = subject

        if subject["data"]["characters"]:
            indexed_json["character_lookup"][subject["object"]][subject["data"]["characters"]] = subject["id"]

        if subject['data'].get('character_images'):
            image_url = subject['data']['character_images'][0]['url']
            downloaded_image_name = _download_image(image_url, images_folder, str(subject['id']))
            subject['data']['character_images'] = [downloaded_image_name]

    print("Saving to app resources...")
    with open(subjects_indexed_file_path, "wt", encoding='utf-8') as fp:
        json.dump(indexed_json, fp, indent=2)

    print("Done!")


