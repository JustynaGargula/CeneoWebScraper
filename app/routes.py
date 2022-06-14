from app import app
from flask import render_template, redirect, url_for, request

from bs4 import BeautifulSoup

from app.models.product import Product
from app.models.opinion import Opinion





@app.route('/')
def index():
    return render_template("index.html.jinja")

@app.route('/extract', methods=["POST", "GET"])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        product = Product(product_id)
        product.extract_product().process_stats().draw_charts()
        product.save_stats()
        product.save_opinions()
        
        
        return redirect(url_for("product", product_id=product_id))
    else:
        return render_template("extract.html.jinja")

@app.route('/products')
def products():
    products = [filename.split(".")[0] for filename in os.listdir("app/opinions")]
    return render_template("products.html.jinja", products=products)

@app.route('/author')
def author():
    return render_template("author.html.jinja")

@app.route('/product/<product_id>')
def product(product_id):
    product = Product(product_id)
    product.read_from_json()
    opinions = product.stats_to_dict()
    # if not os.path.exists("app/static/plots"):
    #     os.makedirs("app/static/plots")

    return render_template("product.html.jinja", stats=stats, product_id=product_id, opinions=opinions)