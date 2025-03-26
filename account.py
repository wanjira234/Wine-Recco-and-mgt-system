from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

account_bp = Blueprint('account', __name__)

# Ensure this function is defined only once
@account_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # ...existing code for updating profile...
        pass
    return render_template('update_profile.html')

# ...existing code...