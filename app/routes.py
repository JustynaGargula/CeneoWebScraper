from app import app
from flask import render_template, redirect
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

@app.route('/')
@app.route('/index')
@app.route('/index/<name>')
def index(name="Hello World"):
    return render_template("index.html.jinja", text=name)

@app.route('/extracts/<product_id>')
def extract(product_id):
    url = "https://www.ceneo.pl/"+product_id+"#tab=reviews"
    all_opinions = []
    while(url):
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        opinions = page.select("div.js_product-review")
        for opinion in opinions:
            
            single_opinion = {
                key: get_item(opinion, *value)                             #ta gwiazdka wypakowuje wartości z listy na osobne zmienne
                    for key, value in selectors.items()
            }
            single_opinion["opinion_id"] = opinion["data-entry-id"]
            all_opinions.append(single_opinion)

        try:
            url = "https://www.ceneo.pl"+get_item(page, "a.paginaton__next", "href")
        except TypeError:
            url = None

    with open("opinions/"+product_id+".json", "w", encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
    return redirect(url_for("product", product_id=product_id))


@app.route('/products')
def products():
    products = [print(*[filename.split(".")[0] for filename in os.listdir("./opinions")])]
    return render_template("products.html.jinja", products=products)

@app.route('/author')


@app.route('/product/,product_id')
def product(product_id):
    opinions = pd.read_json(f"opinions/{product_id}.json")
    opinions.stars = opinions.stars.map(lambda x: float(x.split("/")[0].replace(",", ".")))
    stats = {
                "opinions_count": len(opinions.index),
                "pros_count": opinions.pros.map(bool).sum(),
                "cons_count": opinions.cons.map(bool).sum(),
                "average_score": opinions.stars.mean().round(2)
    }
    

    recommendation = opinions.recommendation.value_counts(dropna = False).sort_index().reindex(["Nie polecam", "Polecam", None])
    recommendation.plot.pie(
        label="", 
        autopct="%1.1f%%", 
        colors=["crimson", "forestgreen", "lightskyblue"],
        labels=["Nie polecam", "Polecam", "Nie mam zdania"]
    )
    plt.title("Rekomendacja")
    plt.savefig(f"plots/{product_id}_recommendations.png")
    plt.close()

    stars = opinions.stars.value_counts().sort_index().reindex(list(np.arange(0,5.5,0.5)), fill_value=0)
    stars.plot.bar()
    plt.title("Oceny produktu")
    plt.xlabel("Liczba gwiazdek")
    plt.ylabel("Liczba opinii")
    plt.grid(True)
    plt.xticks(rotation=0)
    plt.savefig(f"app/static/plots/{product_id}_stars.png")
    plt.close()
        return render_template("products.html.jinja", stats=stats, product_id=product_id, opinions=opinions)


