from flask import Flask, url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    return '''
    <html> 
    <head>
        <link rel="shortcut icon" href="/static/favicon.ico" />
    </head>
    <body>
        <h1> hello world </h1>
        

    </body>
    </html>
    '''
    

