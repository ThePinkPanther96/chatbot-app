from flask import Flask, render_template, request, abort
import openai
import os

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


@app.errorhandler(404)
def not_found(error): 
    return render_template("404.html"), 404


@app.errorhandler(401)
def not_found(error): 
    return render_template("401.html"), 401


@app.route('/500')
def error_500():
    return render_template('500.html'), 500


def get_completion(userText):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are Donald J Trump. You talk like Donald J Trump."
            },
            {
                "role": "user",
                "content": userText
            }
        ]
    )

    return response['choices'][0]['message']['content']


@app.route('/', methods=['GET', 'POST'])
def home():    
    return render_template("index.html")


@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    
    if userText.lower() == "unauthorized":
        abort(401)
    
    try:
        response = get_completion(userText)
    except openai.error.AuthenticationError:
        abort(500) 
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
