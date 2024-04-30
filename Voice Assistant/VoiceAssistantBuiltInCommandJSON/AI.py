import os
import json
from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import pyttsx3
import random
import webbrowser
import threading

app = Flask(__name__)

# Initialize path to the templates folder
TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Set the templates folder for Flask
app.config['TEMPLATES_FOLDER'] = TEMPLATES_FOLDER

# Define the path to the commands JSON file in the templates folder
COMMANDS_FILE = os.path.join(TEMPLATES_FOLDER, 'commands.json')

# Load commands from the JSON file
try:
    with open(COMMANDS_FILE, 'r') as file:
        commands_data = json.load(file)
except FileNotFoundError:
    print(f"Error: {COMMANDS_FILE} not found. Make sure the file exists in the correct location.")
    # Handle the error or exit gracefully

# Print the loaded commands data
#print(commands_data)

# create a text-to-speech object
engine = pyttsx3.init()

# define a function to handle voice commands
def handle_command(command):
    print(f"Handling command: {command}")
    response = "Sorry, I didn't understand that"
    for question, answer in commands_data.items():
        print(f"Comparing with question: {question}")
        if command.lower() == question.lower():
            response = answer
            break  # Exit the loop if a match is found
    print(f"Response: {response}")
    return response



# Function to open the default web browser with index.html
def open_browser():
    webbrowser.open_new_tab('http://127.0.0.1:5000/')

# Route to serve the index.html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def get_command():
    try:
        data = request.get_json()
        command = data['command']
        print(f"Received command: {command}")  # print the command
        assistant_response = handle_command(command)
        response = jsonify({'user': command, 'assistant': assistant_response})
        return response
    except Exception as e:
        # Log the error for debugging
        print(f"Error handling command: {e}")
        return jsonify({'error': str(e)}), 500

# Define route to handle the favicon.ico request
@app.route('/favicon.ico')
def favicon():
    return ''

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        engine.say("Listening...")
        engine.runAndWait()
        # Set a timeout for listening
        r.listen(source, timeout=10)
        print("Listening for 10 seconds or until user speaks...")
        try:
            print("Recognizing...")
            audio = r.listen(source, timeout=10)
            command = r.recognize_google(audio)
            print(f"User said: {command}")
            # Save user's spoken text to JSON file
            save_conversation({'user': command})
            return command
        except sr.WaitTimeoutError:
            print("No user input within 10 seconds.")
            return None
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

