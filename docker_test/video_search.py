import os
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime
from google.cloud import storage
import requests

MAX_UPLOAD_SIZE_MB = 100
MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
UPLOAD_FOLDER = './videos'
ALLOWED_EXTENSIONS = set(['mp4', 'flv', 'avi', 'wmv', 'mov'])  #what extensions should we allow?
BUCKET_NAME = 'uploaded_videos_from_clients'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def main_search():
    return render_template('main_search.html')

def create_bucket():
    """create the bucket named uploaded_videos_from_clients
    to store the uploaded videos
    """
    # Instantiates a client
    storage_client = storage.Client()

    # Creates the new bucket
    bucket = storage_client.create_bucket(BUCKET_NAME)

def list_blobs():
    """Lists all the blobs in the bucket with videos from the client."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)

    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def process_video(file):
    """store the file at filepath and return the path"""
    #do we want to store the video? for now processing the video will just be storing the video in a folder on this server

    #original_filename = secure_filename(file.filename) #original filename, don't know if we want to do anything with original filename
    original_extension = '.' + file.filename.rsplit('.', 1)[1].lower()
    filename = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3] #just make the filename the current time
    filename += original_extension
    save_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # app.logger.debug(save_filepath)
    file.save(save_filepath)

    return (str(save_filepath), str(filename))

#returns whether the uploaded video is valid (it has a valid extension and is not over the size limit)
def file_valid():
    filename = request.files['video'].filename
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
        request.content_length is not None and request.content_length <= MAX_UPLOAD_SIZE


@app.route('/search', methods=['GET', 'POST'])
def search():
    #redirect to main page if there wasn't a valid POST request
    if request.method != 'POST' or \
        'video' not in request.files or \
        request.files['video'] == None or \
        request.files['video'].filename == '':
        return redirect(url_for('main_search'))

    #otherwise the video file was not the right format or too big
    elif(not file_valid()):
        flash('Invalid video. Please a select a video (.mp4, .flv, .avi, .wmv, .mov) at most ' + str(MAX_UPLOAD_SIZE_MB) + 'MB')
        return redirect(url_for('main_search'))

    #if the uploaded file is valid then process the video
    else:
        file = request.files['video']
        saved_filepath, filename = process_video(file)
        upload_blob(saved_filepath, filename) # issue: this file name is not unique for all users
        os.remove(saved_filepath) # only store the file on the cloud
        return render_template('search_results.html', filename = filename)

@app.route('/get_other_results', methods=['POST'])
def get_other():
    # call other microservices
    data = request.get_json()
    uploaded_video_name = data['filename']

    # extract the images
    url_extract_img = 'http://10.39.243.238:80'
    data = {'filename':uploaded_video_name}
    headers = {'Content-type': 'application/json'}
    res_img = requests.post(url_extract_img, json=data, headers=headers)

    # do labeling from the images
    url_labels = 'http://10.39.252.221:80'
    res_labels = requests.post(url_labels, json=data, headers=headers)

    url_text_detect = 'http://10.39.252.215:80'
    res_text = requests.post(url_text_detect, json=data, headers=headers)
    res = res_img.text + ' ' + res_labels.text + ' ' + res_text.text
    return str(res)

app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work

# start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
