import re
import random
from datetime import datetime

# --- Global variable for storing user name ---
user_name = None

# --- Helper Function ---
def get_time():
    return datetime.now().strftime("%H:%M:%S")

def get_date():
    return datetime.now().strftime("%d-%m-%Y")

# --- Chatbot Function ---
def chatbot_response(user_input):
    global user_name
    user_input = user_input.lower().strip()

    # Greeting patterns
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    if any(word in user_input for word in greetings):
        responses = [
            "Hey there! 👋",
            "Hello! How can I assist you today?",
            "Hi! Nice to meet you 😊",
        ]
        return random.choice(responses)

    # Asking for name
    if re.search(r"(my name is|i am|i'm)\s+(\w+)", user_input):
        match = re.search(r"(my name is|i am|i'm)\s+(\w+)", user_input)
        user_name = match.group(2).capitalize()
        return f"Nice to meet you, {user_name}! 😄"

    # Remember name
    if user_name and re.search(r"what is my name", user_input):
        return f"Your name is {user_name}! You already told me 😉"

    # Asking how are you
    if "how are you" in user_input:
        return random.choice([
            "I'm doing great, thanks for asking!",
            "All systems running smoothly ⚙️",
            "I'm fine, how about you?"
        ])

    # Date and time queries
    if "time" in user_input:
        return f"The current time is {get_time()} ⏰"

    if "date" in user_input:
        return f"Today's date is {get_date()} 📅"

    # Weather related
    if "weather" in user_input:
        return "I can't check real-time weather 🌦️, but I hope it's nice where you are!"

    # Chatbot identity
    if "who are you" in user_input or "what are you" in user_input:
        return "I'm a rule-based chatbot built with Python 🤖"

    # Small talk
    if "thank" in user_input:
        return random.choice(["You're welcome 😊", "Anytime!", "Glad I could help!"])

    if "joke" in user_input:
        jokes = [
            "Why did the computer get cold? Because it left its Windows open! 😂",
            "I'm reading a book on anti-gravity — it’s impossible to put down!",
            "Why did the function return early? Because it had a break! 😜"
        ]
        return random.choice(jokes)

    # Exit
    if user_input in ["bye", "exit", "quit", "goodbye"]:
        return "Goodbye! 👋 Hope we chat again soon!"

    # Default fallback
    return random.choice([
        "Hmm... I didn't quite get that 🤔",
        "Could you rephrase that?",
        "I'm not sure I understand, can you try again?"
    ])

# --- Main Chat Loop ---
print("🤖 Chatbot: Hello! I'm your Python chatbot. Type 'bye' to exit.\n")

while True:
    user_message = input("You: ")
    response = chatbot_response(user_message)
    print("🤖 Chatbot:", response)

    if "bye" in user_message.lower():
        break