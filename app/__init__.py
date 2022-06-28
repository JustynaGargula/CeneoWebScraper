from flask import Flask

app = Flask(__name__)

from app import routes
app.config['SECRET_KEY'] = 'Qwerty123!'
app.run(debug=True)