import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from google.cloud import storage
import requests
from cv2 import VideoCapture,CAP_PROP_FRAME_COUNT, imwrite
import random


"""extract images using CV2 randomly but evenly distributed.
The images are uploaded as jpg files to a bucket with the same name as the video.
The images, frames would be deleted.
Chong Tian 5/1/2018
"""
VIDEO_BUCKET_NAME = 'uploaded_videos_from_clients'
UPLOAD_FOLDER = './videos'
IMGS_FOLDER = './imgs'


def extract_img(save_filepath, bucket_name, num=10):
    """evenly capture num of frames from the video"""
    cap = VideoCapture(save_filepath)

    length_video = int(cap.get(CAP_PROP_FRAME_COUNT))
    parts = length_video // num # the part of video that 1 frame extracted
    start_part_num = 0
    currentFrame = 0

    res = []

    for currentFrame in range(length_video):
        if currentFrame == start_part_num:
            add_frame_num = random.randint(start_part_num, start_part_num + parts - 1)
            start_part_num += parts

        if add_frame_num > length_video:
            break

        _,frame = cap.read()

        if currentFrame == add_frame_num:
            img_name = 'frame' + str(currentFrame) + '.jpg'
            save_imgs_filepath = os.path.join(IMGS_FOLDER, img_name)
            imwrite(save_imgs_filepath,frame)
            upload_blob(save_imgs_filepath, img_name, bucket_name)
            os.remove(save_imgs_filepath)

        currentFrame += 1

def create_bucket(bucket_name):
    """Creates a new bucket."""
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)
    # print('Bucket {} created'.format(bucket.name))


def download_blob(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(VIDEO_BUCKET_NAME)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    # print('Blob {} downloaded to {}.'.format(
    #     source_blob_name,
    #     destination_file_name))


def upload_blob(source_file_name, destination_blob_name, bucket_name):
    """Uploads a file to the bucket"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # print('File {} uploaded to {}.'.format(
    #     source_file_name,
    #     destination_blob_name))


app = Flask(__name__)


@app.route("/", methods=['POST'])
def main_search():
    res = request.get_json()
    uploaded_video_name = res['filename']
    save_filepath = os.path.join(UPLOAD_FOLDER, uploaded_video_name)
    download_blob(uploaded_video_name, save_filepath)
    bucket_name = uploaded_video_name.split(".")[0]
    create_bucket(bucket_name)

    # do some calculation here
    extract_img(save_filepath, bucket_name)
    os.remove(save_filepath)
    return "image extraction finished. the images are uploaded to" + str(bucket_name)

app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work

# start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
