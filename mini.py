from flask import Flask, render_template, request, jsonify
from g4f.client import Client
from flask_caching import Cache
import time
from flask_cors import CORS  # Added for CORS
from langdetect import detect, DetectorFactory
import re
import os  # Added to handle dynamic port assignment

# Ensure consistent language detection
DetectorFactory.seed = 0

app = Flask(__name__)

# Enable CORS for the app, allowing requests from any origin
CORS(app)  

# Configure caching
app.config['CACHE_TYPE'] = 'simple'  
cache = Cache(app)

client = Client()

# Predefined responses for specific questions
responses = {
    "WHO ARE YOU": "I’M  UTPC-AI, developed by Reconnect from Tanzania. I’m here to assist with your questions and provide helpful information.",
    "who are you?": "I’m UTPC-AI, developed by Reconnect from Tanzania. I’m here to assist with your questions and provide helpful information.",
    "what is chatgpt": "Hahaha! He might be my brother, but sorry i'd not like to provide any more information about this",
    "who is Chatgpt": "Hahaha! are you kidding me? Why are you asking about him? He might be my brother, but sorry i'd not like to provide any more information about this",
    "what do you know about chatgpt":"Hahaha! are you kidding me? Why are you asking about him? He might be my brother, but sorry i'd not like to provide any more information about this.",
    # UTPC-related responses
    "what is utpc": "UTPC stands for Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what does utpc mean": "UTPC means Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what is the meaning of utpc": "The meaning of UTPC is Union Of Tanzania Press Clubs, focused on enhancing the collaboration and effectiveness of press clubs across Tanzania.",
    # Case with question marks
    "what is utpc?": "UTPC stands for Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what does utpc mean?": "UTPC means Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what is the meaning of utpc?": "The meaning of UTPC is Union Of Tanzania Press Clubs, focused on enhancing the collaboration and effectiveness of press clubs across Tanzania."
}

# Function to format the response for better readability
def format_response(text):
    text = re.sub(r'\n+', '</p><p>', text)  # Replace new lines with paragraph tags
    text = f'<p>{text}</p>'  # Wrap text in <p> tags
    
    # Convert simple text lists into HTML lists
    text = re.sub(r'^(\d+\.)\s+(.*)', r'<li>\2</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\s+(.*)', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', text)
    
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if user_message:
        # Handle UTPC-related responses
        if "utpc" in user_message.lower():
            return jsonify({
                'response': format_response(
                    "The Union of Tanzania Press Clubs (UTPC) is a prominent umbrella organization that represents a diverse network of press clubs across Tanzania..."
                )
            })
            
        if "chatgpt" in user_message.lower():
            return jsonify({
                'response': format_response(
                    "Hahaha! sorry I'd not like to provide any more information about any other chatbots. UTPC-AI is one of the great chatbots, just give me a chance to assist you."
                )
            })

        # Check for predefined responses
        predefined_response = responses.get(user_message.lower())
        if predefined_response:
            formatted_response = format_response(predefined_response)
            return jsonify({'response': formatted_response})

        try:
            # API call for generating responses
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            bot_response = response.choices[0].message.content

            # Replace "chatGPT" with "UTPC-AI"
            bot_response = bot_response.replace("chatGPT", "UTPC-AI")
            bot_response = bot_response.replace("ChatGPT", "UTPC-AI")
            bot_response = bot_response.replace("An error occurred while processing your request.", "Sorry I can't provide")

            # Replace "OpenAI" with "Reconnect"
            bot_response = bot_response.replace("OpenAI", "Reconnect skilled Developer")

            # Detect language and filter responses
            detected_language = detect(bot_response)
            if detected_language not in ['en', 'sw']:
                return jsonify({
                    'response': format_response(
                        "Sorry, I am still under development. Please use Swahili or English."
                    )
                })

            # Format response for readability
            formatted_response = format_response(bot_response)

            return jsonify({'response': formatted_response})
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return jsonify({'response': 'Sorry, I cannot provide information about this.'})
    
    return jsonify({'response': 'No message received'})

if __name__ == "__main__":
    from waitress import serve
    # Use dynamic port, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    serve(app, host='0.0.0.0', port=port, threads=2)
