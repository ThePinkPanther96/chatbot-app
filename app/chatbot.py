from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']


@app.route('/', methods=['GET', 'POST'])
def home():    
    return render_template("index.html")


@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    response = get_completion(userText)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)