from flask import Flask, render_template, request, redirect
from flask_sqalchemy import SQLAlchemy
import re
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///parties.db'
db = SQLAlchemy(app)

class Parties(db.Model):
    id = db.Column(db.String, Primary_key=True, nullable=False)
    party_name = db.Column(db.String(200), nullable=False)
    generated_url = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), nullable=True)
    user_password = db.Column(db.String(200), nullable=True)
    def __repr__(self):
        return '<Name %r>' % self.id

@app.route("/")
def home():
    return render_template('home.html', page_class="home") 
        

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        party_name = request.form['party_name']
        user_email = request.form['user_email']
        generated_url = request.form['generated_url']
        print(generated_url)
        return redirect(f'/{generated_url}', code=303)
    return render_template('signup.html', page_class="signup") 
    
        

if __name__ == "__main__":
    app.run()

