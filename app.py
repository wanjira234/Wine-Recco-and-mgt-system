import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from surprise import Dataset, Reader, KNNBaseline
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '1234444rrttyyujii'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wines.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the Wine model
class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=True)
    variety = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255), nullable=True)
    province = db.Column(db.String(255), nullable=True)
    winery = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    traits = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)  # Store the image filename here


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords securely

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# List of wine traits
all_traits = [
    'almond', 'anise', 'apple', 'apricot', 'baked', 'baking_spices', 'berry', 'black_cherry', 'black_currant',
    'black_pepper', 'black_tea', 'blackberry', 'blueberry', 'boysenberry', 'bramble', 'bright', 'butter',
    'candy', 'caramel', 'cardamom', 'cassis', 'cedar', 'chalk', 'cherry', 'chocolate', 'cinnamon', 'citrus',
    'clean', 'closed', 'clove', 'cocoa', 'coffee', 'cola', 'complex', 'concentrated', 'cranberry', 'cream',
    'crisp', 'dark', 'dark_chocolate', 'dense', 'depth', 'dried_herb', 'dry', 'dust', 'earth', 'edgy',
    'elderberry', 'elegant', 'fennel', 'firm', 'flower', 'forest_floor', 'french_oak', 'fresh', 'fruit',
    'full_bodied', 'game', 'grapefruit', 'graphite', 'green', 'gripping', 'grippy', 'hearty', 'herb',
    'honey', 'honeysuckle', 'jam', 'juicy', 'lavender', 'leafy', 'lean', 'leather', 'lemon', 'lemon_peel',
    'length', 'licorice', 'light_bodied', 'lime', 'lush', 'meaty', 'medium_bodied', 'melon', 'milk_chocolate',
    'minerality', 'mint', 'nutmeg', 'oak', 'olive', 'orange', 'orange_peel', 'peach', 'pear', 'pencil_lead',
    'pepper', 'pine', 'pineapple', 'plum', 'plush', 'polished', 'pomegranate', 'powerful', 'purple',
    'purple_flower', 'raspberry', 'refreshing', 'restrained', 'rich', 'ripe', 'robust', 'rose', 'round',
    'sage', 'salt', 'savory', 'sharp', 'silky', 'smoke', 'smoked_meat', 'smooth', 'soft', 'sparkling',
    'spice', 'steel', 'stone', 'strawberry', 'succulent', 'supple', 'sweet', 'tangy', 'tannin', 'tar',
    'tart', 'tea', 'thick', 'thyme', 'tight', 'toast', 'tobacco', 'tropical_fruit', 'vanilla', 'velvety',
    'vibrant', 'violet', 'warm', 'weight', 'wet_rocks', 'white', 'white_pepper', 'wood'
]


# Helper function to generate random image filenames
def generate_random_image_name():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(8)) + ".jpg"


# Populate the database with wine data (run once)


def populate_database():
    with app.app_context():
        if not Wine.query.first():  # Check if the database is empty
            for _, row in df_wine_combi.iterrows():
                traits_list = [trait for trait in all_traits if row.get(trait, 0) == 1]
                traits_str = ','.join(traits_list)

                # Generate a filename based on the wine title
                wine_name = row['title']
                sanitized_name = wine_name.replace(' ', '_').lower() + ".jpg"  # Replace spaces with underscores
                image_path = os.path.join('static', 'images', sanitized_name)

                # Check if the image exists locally
                if os.path.exists(image_path):
                    image_filename = sanitized_name
                else:
                    image_filename = "download.jpeg"  # Fallback to placeholder image

                wine = Wine(
                    title=row['title'],
                    points=row['points'],
                    price=row['price'],
                    variety=row['variety'],
                    country=row['country'],
                    province=row['province'],
                    winery=row['winery'],
                    description=row['description'],
                    traits=traits_str,
                    image=image_filename
                )
                db.session.add(wine)


            db.session.commit()


# Load wine dataframes
df_wine_model = pd.read_pickle('model_data/df_wine_us_rate.pkl')
df_wine_combi = pd.read_pickle('model_data/df_wine_combi.pkl')

# Initialize the database (run once)
with app.app_context():
    db.drop_all()  # Drop all tables
    db.create_all()  # Recreate tables based on updated models
    populate_database()  # Populate the database with data


# Recommendation function
def recommend_wines(selected_traits):
    reader = Reader(rating_scale=(88, 100))
    data = Dataset.load_from_df(df_wine_model, reader)

    sim_options = {'name': 'cosine'}
    model = KNNBaseline(k=35, min_k=1, sim_options=sim_options, verbose=False)

    train = data.build_full_trainset()
    model.fit(train)

    recommend_list = []
    user_wines = [wine.title for wine in Wine.query.filter_by(taster_name='mockuser').all()]
    not_user_wines = [wine.title for wine in Wine.query.filter(Wine.title.notin_(user_wines)).all()]

    for wine_title in not_user_wines:
        prediction = model.predict(uid='mockuser', iid=wine_title)
        recommend_list.append({'title': prediction.iid, 'est_match_pts': prediction.est})

    recommend_df = pd.DataFrame(recommend_list)

    # Filter wines by selected traits
    trait_filter = ['title'] + selected_traits
    df_temp_traits = df_wine_combi[trait_filter]
    df_temp_traits['sum'] = df_temp_traits.sum(axis=1, numeric_only=True)
    df_temp_traits = df_temp_traits[df_temp_traits['sum'] != 0]

    df_selectrec_temp = df_temp_traits.merge(recommend_df, on='title', how='left')
    df_selectrec_detail = df_selectrec_temp.merge(df_wine_combi, on='title', how='left')
    df_selectrec_detail.drop_duplicates(inplace=True)

    df_rec_final = df_selectrec_detail.sort_values('est_match_pts', ascending=False).head(10)
    return df_rec_final[
        ['title', 'points', 'price', 'variety', 'country', 'province', 'winery', 'description', 'traits']
    ]


# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_traits = request.form.getlist('traits')
        recommendations = recommend_wines(selected_traits)
        return render_template('results.html', recommendations=recommendations)
    return render_template('index.html', all_traits=all_traits)


@app.route('/catalog')
def catalog():
    wines = Wine.query.all()
    return render_template('catalog.html', wines=wines)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    wine_id = int(request.form.get('wine_id'))
    wine = Wine.query.get(wine_id)
    if wine:
        cart = session.get('cart', [])
        cart.append({
            'id': wine.id,
            'title': wine.title, 
            'price': wine.price,
            'traits': wine.traits
        })
        session['cart'] = cart
    return redirect('/catalog')


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] for item in cart_items if item['price'])
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/wine/<int:wine_id>')
def wine_details(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    return render_template('wine_details.html', wine=wine)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/my-account', methods=['GET', 'POST'])
def my_account():
    # Determine the action (login or signup)
    action = request.args.get('action', 'login')

    if request.method == 'POST':
        if action == 'login':
            email = request.form['email']
            password = request.form['password']

            # Perform login validation (e.g., check database)
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):  # Assuming you have a password-checking method
                session['user_id'] = user.id
                return redirect('/')
            else:
                flash("Invalid email or password", "error")
                return render_template('my_account.html', action=action, error="Invalid email or password")

        elif action == 'signup':
            name = request.form['name']
            gender = request.form['gender']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']

            # Save user data to the database
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered", "error")
                return render_template('my_account.html', action=action, error="Email already registered")

            # Create and save the new user
            new_user = User(name=name, gender=gender, phone=phone, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user automatically
            session['user_id'] = new_user.id
            return redirect('/')

    return render_template('my_account.html', action=action)


@app.route('/learn')
def learn():
    return render_template('learn.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        # Perform a case-insensitive search on the wine title
        wines = Wine.query.filter(Wine.title.ilike(f'%{query}%')).all()
    else:
        wines = []
    return render_template('catalog.html', wines=wines)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
