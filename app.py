from flask import Flask, jsonify, render_template
from flask.globals import request
from flask.helpers import flash
from werkzeug.utils import redirect, secure_filename
import os
import boto3


s3 = boto3.resource('s3')
bucket = s3.Bucket('awsdeveloperpavangole')  # Going in the bucket

rek = boto3.client('rekognition', 'ap-south-1')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask("awsapi")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def respond(keyname):
    response = rek.detect_text(
      Image={
          'S3Object': {
              'Bucket': 'awsdeveloperpavangole',
              'Name': keyname
          }
      }
    )
    json = {}
    json['data'] = []
    for data in response['TextDetections']:
        if data['Type'] == 'LINE':
            json['data'].append(data['DetectedText'])
    return json


@app.route('/', methods=['GET'])
def upload_file():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def response_data():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template('flash.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            data = file.read()
            if 'png' in file.filename:
                bucket.put_object(ACL='private', Body=data, Key='file.png')
                data = respond('file.png')
                print(data)
                return render_template('response.html',info = data)
            if 'jpeg' in file.filename:
                bucket.put_object(ACL='private', Body=data, Key='file.jpeg')
                data = respond('file.jpeg')
                return render_template('response.html', info = data)
            if 'jpg' in file.filename:
                bucket.put_object(ACL='private', Body=data, Key='file.jpg')
                data = respond('file.jpg')
                return render_template('response.html', info = data)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run('0.0.0.0')