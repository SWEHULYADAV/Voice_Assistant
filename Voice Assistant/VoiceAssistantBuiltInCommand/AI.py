import os
import json
from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import pyttsx3
import random
import webbrowser
import threading
import requests
from pymongo import MongoClient

app = Flask(__name__)

# Initialize MongoDB client and define collection
client = MongoClient('mongodb://localhost:27017/')
db = client['conversation_db']
collection = db['conversations']

# create a text-to-speech object
engine = pyttsx3.init()

# define a function to handle voice commands
def handle_command(command):
    assistant_response = ""
    if command == "hello":
        assistant_response = "Hello, how are you?"
    elif command == "what is your name":
        assistant_response = "My name is Ihana. Nice to meet you!"
    elif command == "tell me a joke":
        jokes = ["Why was the math book sad? Because it had too many problems.", "Why did the computer go to the doctor? It had a virus.", "What do you call a fake noodle? An impasta."]
        assistant_response = random.choice(jokes)
    elif command == "give me an interesting fact":
        facts = ["The shortest war in history was between Britain and Zanzibar on August 27, 1896, and lasted only 38 minutes.", "The longest word in the English language, according to the Oxford English Dictionary, is pneumonoultramicroscopicsilicovolcanoconiosis.", "The human nose can detect over 1 trillion different scents."]
        assistant_response = random.choice(facts)
    elif command.startswith("calculate"):
        expression = command[len("calculate"):].strip()
        try:
            result = eval(expression)
            assistant_response = f"The result of {expression} is {result}"
        except Exception as e:
            assistant_response = f"Sorry, I couldn't calculate that: {str(e)}"
    elif command.startswith("convert"):
        conversion = command[len("convert"):].strip()
        try:
            parts = conversion.split("to")
            from_unit = parts[0].strip()
            to_unit = parts[1].strip()
            if from_unit == "kilograms" and to_unit == "pounds":
                # Conversion logic
                pass
            elif from_unit == "pounds" and to_unit == "kilograms":
                # Conversion logic
                pass
            else:
                assistant_response = "Sorry, I can't perform that conversion"
        except Exception as e:
            assistant_response = f"Sorry, I couldn't perform the conversion: {str(e)}"
    else:
        assistant_response = "Sorry, I didn't understand that"
    # Speak the assistant's response
    engine.say(assistant_response)
    engine.runAndWait()
    return assistant_response

# Function to open the default web browser with index.html
def open_browser():
    webbrowser.open_new_tab('http://127.0.0.1:5000/')

# Route to serve the index.html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def get_command():
    data = request.get_json()
    command = data['command']
    assistant_response = handle_command(command)
    return jsonify({'user': command, 'assistant': assistant_response})

# Define route to handle the favicon.ico request
@app.route('/favicon.ico')
def favicon():
    return ''

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        print("Recognizing...")
        command = r.recognize_google(audio)
        print(f"User said: {command}")
        # Save user's spoken text to JSON file
        save_conversation({'user': command})
        return command
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_conversation(data):
    filepath = os.path.join(os.path.dirname(__file__), 'conversation.json')
    with open(filepath, 'a') as file:
        json.dump(data, file)
        file.write('\n')

def get_weather(city):
    api_key = 'dda44e91cda7419fafc214001242904'
    url = f'https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no'
    response = requests.get(url)
    data = response.json()
    if 'error' not in data:
        weather_desc = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        return f"The weather in {city} is {weather_desc} with a temperature of {temp_c}°C."
    else:
        return "Sorry, I couldn't fetch the weather information for that location."

@app.route('/weather', methods=['POST'])
def weather_forecast():
    data = request.get_json()
    city = data['city']
    weather_info = get_weather(city)
    engine.say(weather_info)
    engine.runAndWait()
    return 'Weather forecast processed successfully'

@app.route('/save-conversation', methods=['POST'])
def save_conversation_route():
    data = request.get_json()
    save_conversation(data)
    return 'Conversation saved successfully', 200

if __name__ == '__main__':
    # Open the web browser in a new thread
    threading.Thread(target=open_browser).start()
    # Run the Flask app
    app.run(debug=True)
