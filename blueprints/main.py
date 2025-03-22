from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html', now=datetime.utcnow())

@main_bp.route('/catalog')
def catalog():
    return render_template('catalog.html')

@main_bp.route('/welcome')
@login_required
def welcome():
    return render_template('main/welcome.html') 