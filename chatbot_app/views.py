import nltk
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('vader_lexicon')
from django.http import HttpResponse
from django.shortcuts import render
from .models import Conversation
from .intents import intents
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import random
import text2emotion
lemmatizer = WordNetLemmatizer()

def home(request):
    return render(request,"index.html")

def chatbot_response(msg):
    words = word_tokenize(msg)
    words = [lemmatizer.lemmatize(word) for word in words]
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            tokenized_pattern = word_tokenize(pattern)
            tokenized_pattern = [lemmatizer.lemmatize(word) for word in tokenized_pattern]
            if all(word in words for word in tokenized_pattern):
                return random.choice(intent['responses'])
    return "I didn't understand that. Please try again."

emotion_labels = {
    'Happy': 'happy',
    'Angry': 'angry',
    'Sad': 'sad',
    'Fear': 'bad',
    'Surprise': 'surprised'
}

def analyze_emotion(msg):
    emotions = text2emotion.get_emotion(msg)
    max_emotion = max(emotions, key=emotions.get)
    return emotion_labels[max_emotion]

def chat(request):
    msg = request.GET.get('user_message')
    msg1=msg.lower()
    response = chatbot_response(msg1)
    emotion = analyze_emotion(msg1)
    print(emotion)
    Conversation.objects.create(user_input=msg, response=response)
    return HttpResponse(response)