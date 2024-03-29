import os
from flask import Flask, request
from google.cloud import storage
import requests
from google.cloud import vision
from google.cloud.vision import types

"""use the google vision api to recognize faces in the images
Chong Tian 5/2/2018
"""
IMGS_FOLDER = './imgs'


def face_recog():
    """recognize faces in one image"""
    client = vision.ImageAnnotatorClient()

    imgs = os.listdir(IMGS_FOLDER)
    res=[]
    for img in imgs:
        img_path = IMGS_FOLDER + '/' +img
        with open(img_path, 'rb') as image_file:
            content = image_file.read()

            image = types.Image(content=content)

            response = client.label_detection(image=image)
            labels = response.label_annotations



            for label in labels:
                res.append(label.description)
    return res


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
    results = face_recog()
    delete_imgs()
    return ', '.join(map(str, results))

app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work

# start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
