from flask import render_template
from app import app, db

@app.errorhandler(Exception)
def generic_error(error):
    return render_template('generic_error.html')