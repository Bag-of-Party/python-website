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
        print(party_name, user_email)
        party_name = re.sub(r'[^a-z0-9]+', '-', party_name.lower()) 
        random_prefix = ''.join([
            random.choice(string.ascii_letters), 
            str(random.choice(range(0,9))), 
            random.choice(string.ascii_letters), 
            str(random.choice(range(0,9)))
        ])
        slug = f"{random_prefix}/{party_name}"
        return redirect(f'/{slug}', code=303)
    return render_template('signup.html', page_class="signup") 
    
        

if __name__ == "__main__":
    app.run()

