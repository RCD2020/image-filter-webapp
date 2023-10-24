import os
from flask import (
    flash, Flask, redirect, render_template, request, url_for
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
from imgfilter import ImgFilter

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


def source_path(filename):
    return f'{app.config["UPLOAD_FOLDER"]}/{filename}'


@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
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
            file.save(source_path(filename))
            return redirect(url_for(
                'filter_page',
                filename=filename
            ))
        else:
            flash('Invalid file type.')
            return redirect('/')

    return render_template('index.html')


@app.route('/filter')
def filter_noargs():
    flash('Must have image name in url')
    return redirect('/')


@app.route('/filter/<filename>')
def filter_page(filename):
    height, width = 0,0
    try:
        with Image.open(source_path(filename)) as img:
            width, height = img.size
    except:
        flash(f'Could not open {filename}')
        return redirect('/')

    factor = 300 / min(width, height)
    width *= factor
    height *= factor

    return render_template(
        'filter.html', path=filename, height=height, width=width
    )
    

@app.route('/filtered', methods=['POST'])
def filtered_page():
    filter_text = request.form.get('filter-text')
    filename = request.form.get('filename')

    if filter_text == '':
        flash('No filter provided')
        return redirect(url_for(
            'filter_page', filename=filename
        ))
    
    filter_text = filter_text.replace('\r', '\n')
    # print(filter_text)
    # splittee = filter_text.split('\n')
    # for x in range(len(splittee)):
    #     for y in range(len(splittee[x])):
    #         print(x + y, splittee[x][y], ord(splittee[x][y]))
    
    imgFilter = ImgFilter(filename)
    imgFilter(filter_text)

    height = imgFilter.height
    width = imgFilter.width
    
    factor = 750 / max(width, height)
    width *= factor
    height *= factor
    
    return render_template(
        'filtered.html', path=filename, width=width, height=height
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='7272')
