import os
from flask import Flask, request, render_template
from google.cloud import storage
import requests
from flask_socketio import SocketIO

"""use the google vision api to recognize faces in the images
Chong Tian 5/2/2018
"""

app = Flask(__name__)
app.secret_key = '\x1d%oW\x81w\xefH\xbf\xb6\xb0\xd3\xd6_?\x8f\x8b,\xd7\xaa;\xbc/\xd4' #this line is so we can use sessions, which is neccessary for flashes to work
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@app.route("/", methods=['GET'])
def main_search():
    filename = "po"
    return render_template('main_search.html')


# start the server
if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', port=5000)
