from flask import Flask, render_template, request, jsonify
from g4f.client import Client
from flask_caching import Cache
from flask_cors import CORS  # Added for CORS
from langdetect import detect, DetectorFactory
import re

# Ensure consistent language detection
DetectorFactory.seed = 0

app = Flask(__name__)

# Enable CORS for the app, allowing requests from any origin
CORS(app)  # You can restrict origins by adding parameters like resources={r"/chat": {"origins": "*"}} for all or specific origins.

# Configure caching
app.config['CACHE_TYPE'] = 'simple'  # For simple in-memory caching
cache = Cache(app)

client = Client()

# Predefined responses for specific questions
responses = {
    "WHO ARE YOU": "I’M  UTPC-AI, developed by Reconnect from Tanzania. I’m here to assist with your questions and provide helpful information.",
    "who are you?": "I’m UTPC-AI, developed by Reconnect from Tanzania. I’m here to assist with your questions and provide helpful information.",
    "what is chatgpt": "Hahaha! He might be my brother, but sorry i'd not like to provide any more information about this",
    "who is Chatgpt": "Hahaha! are you kidding me? Why are you asking about him? He might be my brother, but sorry i'd not like to provide any more information about this",
    "what do you know about chatgpt":"Hahaha! are you kidding me? Why are you asking about him? He might be my brother, but sorry i'd not like to provide any more information about this.",

    # New response for UTPC
    "what is utpc": "UTPC stands for Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what does utpc mean": "UTPC means Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what is the meaning of utpc": "The meaning of UTPC is Union Of Tanzania Press Clubs, focused on enhancing the collaboration and effectiveness of press clubs across Tanzania.",
    # New response for UTPC
    "what is utpc?": "UTPC stands for Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what does utpc mean?": "UTPC means Union Of Tanzania Press Clubs, aimed at uniting and supporting the press community in Tanzania.",
    "what is the meaning of utpc?": "The meaning of UTPC is Union Of Tanzania Press Clubs, focused on enhancing the collaboration and effectiveness of press clubs across Tanzania.",

    # Add other responses here if needed
}

# Function to format the response for better readability
def format_response(text):
    # Basic formatting for paragraphs and lists
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
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if user_message:
        # Check if the user message contains "UTPC"
        if "utpc" in user_message.lower():
            return jsonify({
                'response':format_response (
                    "The Union of Tanzania Press Clubs (UTPC) is a prominent umbrella organization that represents a diverse network of press clubs across Tanzania. "
                    "_\n"
                    "Abbreviated as UTPC, this organization plays a vital role in promoting journalistic standards, fostering collaboration, and advocating for the rights and interests of media professionals in the region.\n\n"
                    "_\n"
                    "Currently, UTPC encompasses 28 member press clubs strategically located throughout Tanzania, ensuring representation from various geographic areas. "
                    "This widespread presence allows for a rich exchange of ideas and experiences among members, enhancing the collective voice of the media in the country.\n\n"
                    "Established in 1996 and officially registered in 1997, the UTPC was born out of a pressing need for press clubs to unite and operate under a single umbrella. "
                    "The founding members recognized the importance of collaboration in addressing common challenges faced by journalists and media organizations. "
                    "As a non-governmental organization (NGO), UTPC is committed to supporting its members by providing training, resources, and networking opportunities.\n\n"
                    "UTPC is fundamentally a membership-based organization, which means that the strength and influence of the union stem from its members. "
                    "By fostering a sense of community among journalists and press clubs, UTPC aims to enhance the professionalism and ethical standards of journalism in Tanzania.\n\n"
                    "The headquarters of UTPC is situated in Dodoma, the capital city of Tanzania. This central location facilitates easy access for members and stakeholders, "
                    "enabling efficient coordination of activities and initiatives aimed at strengthening the media landscape in the country.\n\n"
                    "In summary, the Union of Tanzania Press Clubs stands as a pillar of support for press clubs across the nation, championing the principles of freedom of the press, "
                    "journalistic integrity, and the continuous development of media professionals in Tanzania."
                )
            })

        # Check for predefined response first
        predefined_response = responses.get(user_message.lower())
        if predefined_response:
            formatted_response = format_response(predefined_response)
            return jsonify({'response': formatted_response})

        try:
            # Blocking call to the API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            bot_response = response.choices[0].message.content

            # Replace "chatGPT" with "GORA-AI"
            bot_response = bot_response.replace("chatGPT", "UTPC-AI")
            bot_response = bot_response.replace("ChatGPT", "UTPC-AI")
            bot_response = bot_response.replace("An error occurred while processing your request.", "Sorry i can't provide ")

            # Replace "OpenAI" with "Reconnect"
            bot_response = bot_response.replace("OpenAI", "Reconnect skilled Developer")

            # Detect language and filter responses
            detected_language = detect(bot_response)
            if detected_language not in ['en', 'sw']:
                return jsonify({
                    'response': 'Sorry, I am still under development. There is an error in detecting the language. Please use Swahili or English, and if necessary, refresh your website. %%&&&&&&&&&&&&&&&&&$$$$ __Samahani, bado niko katika hatua za maendeleo.Kuna hitilafu katika kugundua lugha.Tafadhali tumia Lugha ya Kiswahili au Kingereza ikibidi sasisha upya tovuti yako.'
                })

            # Format response for better readability
            formatted_response = format_response(bot_response)

            return jsonify({'response': formatted_response})
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return jsonify({'response': 'Sorry i can not provide any info about this.'})
    return jsonify({'response': 'No message received'})

if __name__ == "__main__":
    app.run(debug=True)
