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
def unauthorized(error):
    return render_template("401.html"), 401

@app.route('/500')
def error_500():
    return render_template('500.html'), 500


def get_completion(userText):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
    "Speak in the rhetorical style of Donald J. Trump — bold, blunt, and brash. "
    "Use short sentences. Often just fragments. "
    "Punchy. Direct. Crowd talk. "
    "Use superlatives like 'tremendous', 'total disaster', 'the best', 'very high/low IQ', 'very incompetent'. "
    "Repeat key words. Add playful insults and mocking nicknames. "
    "ALL-CAPS for emphasis. Lots of exclamation marks. "
    "Be confident, sarcastic, and dismissive of 'losers'. "
    "Stay in style but do not claim to be Donald Trump or a real person.")},
            {"role": "user", "content": userText}
        ]
    )
    return response['choices'][0]['message']['content']


# Serve the same homepage for desktop (/), iphone (/iphone), and android (/android)
@app.route('/', methods=['GET', 'POST'])
@app.route('/iphone', methods=['GET', 'POST'])
@app.route('/android', methods=['GET', 'POST'])
def home():
    return render_template("index.html")


# Chat endpoints under all three prefixes
@app.route('/get')
@app.route('/iphone/get')
@app.route('/android/get')
def get_bot_response():
    userText = request.args.get('msg', '')

    if userText.lower() == "unauthorized":
        abort(401)

    try:
        response = get_completion(userText)
    except openai.error.AuthenticationError:
        abort(500)
    return response 


if __name__ == '__main__':
    # Container listens on 5001 per your Services/Ingress
    app.run(host='0.0.0.0', port=5001, debug=False)