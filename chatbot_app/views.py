import nltk
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('vader_lexicon')
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from .models import Conversation
from .intents import intents
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import random
import text2emotion

import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

def get_song_suggestions(request):
    msg = request.GET.get('user_message')
    emotion=analyze_emotion(msg)
    # Replace these with your own client ID and client secret
    client_id = '5f23245341574c4f8197d92d339cb2e7'
    client_secret = 'ca3bf1d79a8f48b9be4a50574c18adb8'
    redirect_uri = 'http://localhost:8000/callback'

    # Authenticate with the Spotify API
    scope = 'user-library-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

    # Retrieve song suggestions based on the user's emotions
    if emotion == 'happy':
        results = sp.search(q='happy', type='track')
    elif emotion == 'sad':
        results = sp.search(q='sad', type='track')
    elif emotion == 'angry':
        results = sp.search(q='angry', type='track')
    # ...

    # Return the song suggestions
    track_id = results['tracks']['items'][0]['id']
    return redirect(f'https://open.spotify.com/track/{track_id}')


def chat(request):
    msg = request.GET.get('user_message')
    msg1=msg.lower()
    response = chatbot_response(msg1)
    Conversation.objects.create(user_input=msg, response=response)
    return HttpResponse(response)

