import os
from flask import (
    flash, Flask, redirect, render_template, request, url_for
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image

# Load .env file
load_dotenv()

# Restraints and paths for image uploads
UPLOAD_FOLDER = 'static/images/source'
ALLOWED_EXTENSIONS = {'png'}

# initialize the app and configure the upload folder
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('FLASK_SECRET_KEY')


# check if file is correct type
def allowed_file(filename):
    return '.' in filename \
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def landing():
    return render_template('index.html')


@app.route('/filter', methods=['POST'])
def filter_page():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('Must be a .png file.')
        return redirect('/')
    
    # get POSTed file
    file = request.files['file']

    # check if anything was POSTed
    if file.filename == '':
        flash('No selected file.')
        return redirect('/')
    
    # check that there is a file and is allowed type
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(
            os.path.join(app.config['UPLOAD_FOLDER'], filename)
        )
        return render_template(
            'filter.html',
            path=f'{app.config["UPLOAD_FOLDER"]}/{filename}'
        )
    else:
        flash('Invalid file type.')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
