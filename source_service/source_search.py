import os
from flask import Flask, request
from google.cloud import storage
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

"""use the images on google bucket to search source (similar youtube videos)
Chong Tian 5/2/2018
"""
IMGS_FOLDER = './imgs'
SEARCH_URL = 'http://www.google.hr/searchbyimage/upload'


def find_source_from_one_image(fetchUrl, num=3):
    """use selenium to figure the source of the videoselfself.
    Each image is used once and the results are combined.
    The source would be the top 3 links from the google image search.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(executable_path='./chromedriver',chrome_options=chrome_options)
    driver.get(fetchUrl)
    elements = driver.find_elements_by_class_name("iUh30")
    element_list = []

    for element in elements:
        element_list.append(element.text)
    return element_list[0:3]

def find_source(num=3):
    from collections import Counter
    link_count = {}
    imgs = os.listdir(IMGS_FOLDER)
    for img in imgs:
        img_path = IMGS_FOLDER + '/' +img
        with open(img_path, 'rb') as f:
                multipart = {'encoded_image': f, 'image_content': ''}
                response = requests.post(SEARCH_URL, files=multipart, allow_redirects=False)
                fetchUrl = response.headers['Location']
                cur_list = find_source_from_one_image(fetchUrl, num=3)
                cur_dict = Counter(cur_list)
                for k,v in cur_dict.items():
                    if k in link_count:
                        link_count[k] += v
                    else:
                        link_count[k] = v

    res = []
    for key, value in sorted(link_count.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        res.append(key)
    return res[0:num]

def delete_imgs():
    imgs = os.listdir(IMGS_FOLDER)
    for img in imgs:
        img_path = IMGS_FOLDER + '/' +img
        os.remove(img_path)


def download_blob(source_bucket_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(source_bucket_name)
    blobs = bucket.list_blobs()

    for blob in blobs:
        blob = bucket.blob(blob.name)
        destination_file_name =os.path.join(IMGS_FOLDER, blob.name)
        blob.download_to_filename(destination_file_name)

    # print('Blob {} downloaded to {}.'.format(
    #     source_blob_name,
    #     destination_file_name))

app = Flask(__name__)


@app.route("/", methods=['POST'])
def main_search():
    res = request.get_json()
    uploaded_video_name = res['filename']
    save_filepath = os.path.join(IMGS_FOLDER, "")
    bucket_name = uploaded_video_name.split(".")[0]
    download_blob(bucket_name, save_filepath) # download to imgs folder

    # do some calculation here
    results = find_source()
    delete_imgs()
    return ', '.join(map(str, results))

app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work

# start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
