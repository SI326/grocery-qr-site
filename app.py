from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import qrcode, os
from bson import ObjectId

app = Flask(__name__)

# --- MongoDB Connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client["grocery_shop"]
products = db["products"]

# --- Folder for QR codes ---
QR_FOLDER = "static/qr"
os.makedirs(QR_FOLDER, exist_ok=True)

# --- Home Page: Add Products ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']
        product = {"name": name, "price": price, "quantity": quantity}
        inserted = products.insert_one(product)
        product_id = str(inserted.inserted_id)
        qr_url = f"http://localhost:5000/product/{product_id}"
        img = qrcode.make(qr_url)
        qr_path = os.path.join(QR_FOLDER, f"{product_id}.png")
        img.save(qr_path)
        products.update_one({"_id": inserted.inserted_id}, {"$set": {"qr_path": qr_path}})
        return redirect(url_for('index'))
    all_products = list(products.find())
    return render_template('index.html', products=all_products)

@app.route('/product/<id>')
def product_page(id):
    product = products.find_one({"_id": ObjectId(id)})
    if not product:
        return "Product not found", 404
    return render_template('product.html', product=product)

if __name__ == '__main__':
    app.run(debug=True)
