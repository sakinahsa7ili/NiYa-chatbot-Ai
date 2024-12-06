from flask import Flask, render_template, request, jsonify
import openai
import time
import threading

#api key
last_request_time = time.time()
lock = threading.Lock()

app = Flask(__name__)

chat_messages = []
chatbot_ui = None  # Global variable to store ChatbotGUI instance

class ChatbotGUI:
    conversation_history = ""

    @staticmethod
    def display_message(message, is_user_input=False):
        # Implement this method to display messages in your UI
        pass

    @staticmethod
    def is_mental_health_related(text):
        mental_health_keywords = ["greet", "hello", "hi", "hey", "okay", "yes", "yeah", "sure", "mean by", "spend time", "thank you", "thanks",
                                  "positive", "help", "advice", "listen to me", "hear me out", "overcome",
                                  "mental health", "depression","anxiety", "panic attack", "insecure", "depress", "mood disorders",
                                  "psychotic disorders", "obsessive-compulsive disorders", "ocd", "trauma-related disorders", "ptsd",
                                  "eating disorders", "attention-deficit hyperactivity disorders", "adhd", "personality disorders",
                                  "substance-related", "addictive disorders", "neurodevelopmental disorders", "sleep disorders", "insomnia",
                                  "dissociative disorders", "D.I.D", "gender dysphoria", "factitious disorder", "trichotilliomania", "symptom", "symptoms",
                                  "negative","hates me", "disappointed", "upset", "failed", "disorder", "sleep apnea", "restless legs syndrome",
                                  "narcolepsy", "feelings", "suicidal", "die", "stress", "emotional support", "cope", "loss", "fashion", "mental illness",
                                  "seasonal depression", "anxious", "anxiousness", "phobias", "schizophrenia", "dysmorphia", "Delusions", "psychology",
                                  "Bipolar disorder", "Self-care", "Mindfulness", "Meditation", "Psychiatry", "Therapy", "Burnout", "Resilience",
                                  "Stigma", "empathy", "Sleep hygiene", "Social anxiety", "trauma", "recovery", "self-esteem", "self-harm", "rehab", "Rehabilitation",
                                  "Grief", "Self-reflection", "cognitive behavioral therapy", "selective mutism", "Separation Anxiety Disorder", "bye"]
        return any(keyword in text.lower() for keyword in mental_health_keywords)
    
def rate_limited_mental_health_chatbot(prompt):
    global last_request_time
    with lock:
        elapsed_time = time.time() - last_request_time
        if elapsed_time < 5:
            time.sleep(5 - elapsed_time)
        last_request_time = time.time()

    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/chatbot')
def chatbot():
    global chatbot_ui
    # Initial prompt
    initial_prompt = "This chat is a professional session about mental health care. If you have any curiosity about mental health,kindly ask your question and niya will try her best to help you"
    return render_template('chatbot.html', chat_messages=chat_messages, initial_prompt=initial_prompt)


@app.route('/send_message', methods=['POST'])
def send_message():
    global last_request_time, chatbot_ui
    user_input_text = request.json['user_input']

    if not user_input_text.strip():
        return jsonify({'response': 'pardon?'})

    if chatbot_ui is None:
        chatbot_ui = ChatbotGUI()

    if not chatbot_ui.is_mental_health_related(user_input_text):
        return jsonify({'response': 'Sorry dear, but I am here to help with mental health. Please ask a related question.'})
    else:
        # Update the conversation history with the user's input
        chatbot_ui.conversation_history += f"You: {user_input_text}\n\n"

        # Update the prompt with the conversation history
        prompt = chatbot_ui.conversation_history + "NiYa:"

        # Get the response from the chatbot
        response = rate_limited_mental_health_chatbot(prompt)

        # Update the conversation history with the chatbot's response
        chatbot_ui.conversation_history += f"NiYa: {response}\n\n"

    # Display the conversation in the UI
    chatbot_ui.display_message(f"You: {user_input_text}\n", is_user_input=True)
    chatbot_ui.display_message(f"NiYa: {response}\n", is_user_input=False)

    return jsonify({'response': response})    


if __name__ == '__main__':
    app.run(debug=True)
