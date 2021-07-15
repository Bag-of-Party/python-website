from flask import Flask, render_template, request, redirect
import re
import random
import string

app = Flask(__name__)

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

