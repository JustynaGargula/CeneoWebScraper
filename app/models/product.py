import requests
import os
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from app.utils import get_item
from app.models.opinion import Opinion
from matplotlib import pyplot as plt

class Product:
    def __init__(self, product_id=0, opinions=None, product_name="", opinions_count=0, pros_count=0, cons_count=0, average_score=0):
        self.product_id = product_id
        self.product_name = product_name
        if opinions:
            self.opinions = opinions
        else:
            self.opinions = []
        self.opinions_count = opinions_count
        self.pros_count = pros_count
        self.cons_count = cons_count
        self.average_score = average_score
    
    def __str__(self):
        return f"Product: {self.product_id}, {self.opinions}, {self.product_name}, {self.opinions_count}, {self.pros_count}, {self.cons_count}, {self.average_score}"

    def __repr__(self):
        return f"Product: {self.product_id}, {self.opinions}, {self.product_name}, {self.opinions_count}, {self.pros_count}, {self.cons_count}, {self.average_score}"

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "opinions_count": self.opinions_count,
            "pros_count": self.pros_count,
            "cons_count": self.cons_count,
            "average_score": self.average_score,
            "opinions": [opinion.to_dict() for opinion in self.opinions]
        }

    def stats_to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "opinions_count": self.opinions_count,
            "pros_count": self.pros_count,
            "cons_count": self.cons_count,
            "average_score": self.average_score
        }
    
    def opinions_to_dict(self):
        return [opinion.to_dict() for opinion in self.opinions]

    def extract_product(self):
        url = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        self.product_name = get_item(page, "h1.product-top__product-info__name")
        while(url):
            response = requests.get(url)
            page = BeautifulSoup(response.text, 'html.parser')
            opinions = page.select("div.js_product-review")
            for opinion in opinions:
                self.opinions.append(Opinion().extract_opinion(opinion))
            try:    
                url = "https://www.ceneo.pl"+get_item(page,"a.pagination__next","href")
            except TypeError:
                url = None
        return self
    
    def opinions_do_df(self):
        opinions = pd.read_json(json.dumps([opinion.to_dict() for opinion in self.opinions]))
        opinions.stars = opinions.stars.map(lambda x: float(x.split("/")[0].replace(",", ".")))
        return opinions
    
    def process_stats(self):
        if not self.opinions_do_df().empty:
            self.opinions_count = int(self.opinions_do_df().shape[0],)
            self.pros_count = int(self.opinions_do_df().pros.map(bool).sum())
            self.cons_count = int(self.opinions_do_df().cons.map(bool).sum())
            self.average_score = self.opinions_do_df().stars.mean().round(2)
        return self

    def draw_charts(self): 
        self.save_stats()
        recommendation = self.opinions_do_df().recommendation.value_counts(dropna = False).sort_index().reindex(["Nie polecam", "Polecam", None])
        recommendation.plot.pie(
            label="", 
            autopct="%1.1f%%", 
            colors=["crimson", "forestgreen", "lightskyblue"],
            labels=["Nie polecam", "Polecam", "Nie mam zdania"]
        )
        plt.title("Rekomendacja")
        if not os.path.exists("app/static/plots"):
            os.makedirs("app/static/plots")
        plt.savefig(f"app/static/plots/{self.product_id}_recommendations.png")
        plt.close()
        
        stars = self.opinions_do_df().stars.value_counts().sort_index().reindex(list(np.arange(0,5.5,0.5)), fill_value=0)
        stars.plot.bar()
        plt.title("Oceny produktu")
        plt.xlabel("Liczba gwiazdek")
        plt.ylabel("Liczba opinii")
        plt.grid(True)
        plt.xticks(rotation=0)
        plt.savefig(f"app/static/plots/{self.product_id}_stars.png")
        plt.close()

    def save_opinions(self):        
        if not os.path.exists("app/opinions"):
            os.makedirs("app/opinions")
        with open(f"app/opinions/{self.product_id}.json", "w", encoding="UTF-8") as jf:
            json.dump(self.opinions_to_dict(), jf, indent=4, ensure_ascii=False)
    
    def save_stats(self):        
        if not os.path.exists("app/products"):
            os.makedirs("app/products")
        with open(f"app/products/{self.product_id}.json", "w", encoding="UTF-8") as jf:
            json.dump(self.stats_to_dict(), jf, indent=4, ensure_ascii=False)

    def read_from_json(self):
        with open(f"app/products/{self.product_id}.json", "r", encoding="UTF-8") as jf:
            product = json.load(jf)
        self.product_id = product["product_id"]
        self.product_name = product["product_name"]
        self.opinions_count = product["opinions_count"]
        self.pros_count = product["pros_count"]
        self.cons_count = product["cons_count"]
        self.average_score = product["average_score"]
        with open(f"app/opinions/{self.product_id}.json", "r", encoding="UTF-8") as jf:
            opinions = json.load(jf)
        for opinion in opinions:
            self.opinions.append(Opinion(**opinion))
        