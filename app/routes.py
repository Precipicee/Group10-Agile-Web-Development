from app import app
from flask import render_template, request, redirect, url_for

@app.route('/')
@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/visualise')
def visualise():
    return render_template('visualise.html')

@app.route('/share')
def share():
    return render_template('share.html')
