from flask import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
# database configuration---------------------------------------
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ecom"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define your model class for the 'signup' table
class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# function for recommendations



def content_based_recommendations(train_data, item_name, top_n=10):
    if item_name not in train_data['Name'].values:
        print(f"Item '{item_name}' not found in the training data.")
        return pd.DataFrame()
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])
    cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)
    item_index = train_data[train_data['Name'] == item_name].index[0]
    similar_items = list(enumerate(cosine_similarities_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)
    top_similar_items = similar_items[1:top_n+1]
    recommended_item_indices = [x[0] for x in top_similar_items]
    recommended_items_details = train_data.iloc[recommended_item_indices][['Name','Price' ,'ReviewCount', 'Brand', 'ImageURL', 'Rating']]
    return recommended_items_details

# Load CSV files
try:
    trending_products = pd.read_csv('models/trending_products.csv')
    train_data = pd.read_csv('models/clean_data.csv')
except FileNotFoundError:
    print("Error: CSV files not found. Ensure correct file paths.")
    trending_products = pd.DataFrame(columns=['product_name'])  # Provide empty DataFrame with required columns
    train_data = pd.DataFrame()


# Truncate function to limit text length
def truncate(text, length):
    return text[:length] + '...' if len(text) > length else text

# Predefined product images for trending section
random_image_urls = [
    "static/img_1.png", "static/img_2.png", "static/img_3.png",
    "static/img_4.png", "static/img_5.png", "static/img_6.png",
    "static/img_7.png", "static/img_8.png"
]

prices = [40, 50, 23, 34, 45, 56, 67, 78]

def get_random_products():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    random_prices = [random.choice(prices) for _ in range(8)]  # Fix: Generate multiple prices
    return random_product_image_urls, random_prices

@app.route('/')
def index():
    random_product_image_urls, random_prices = get_random_products()
    return render_template('index.html', trending_products=trending_products.head(8),
                           truncate=truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_prices=random_prices)

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/home')
def home():
    random_product_image_urls, random_prices = get_random_products()
    return render_template('index.html', trending_products=trending_products.head(8),
                           truncate=truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_prices=random_prices)

@app.route('/signup' ,methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        new_signup = Signup(username = username, email = email, password = password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed up successfully!'
                               )
    
@app.route('/signin' ,methods=['POST','GET'])
def signin():
    if request.method == 'POST':
        username = request.form.get('signinUsername')
        password = request.form.get('signinPassword')

        new_signin = Signin(username = username, password = password)
        db.session.add(new_signin)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html',username=username,
                               trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed in successfully!'
                               )


@app.route('/recommendations', methods=['POST','GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('prod')
        # prod = request.form.get('OPI Infinite Shine, Nail Lacquer Nail Polish, Bubble Bath')
        content_based_record = content_based_recommendations(train_data,prod)

        if content_based_record.empty:
            message = "No Recommendation avaible for this product."
            return render_template('main.html', message = message)
        else:
            random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
            print(content_based_record, random_product_image_urls)
            return render_template('main.html',content_based_record=content_based_record,
                                   random_product_image_urls=random_product_image_urls,
                                   random_price=random.choice(price))


if __name__ == '__main__':
    app.run(debug=True)
