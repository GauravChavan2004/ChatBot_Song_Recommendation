import nltk
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('vader_lexicon')
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from .models import Conversation
from .models import Emotion
from .intents import intents
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import random
import text2emotion as te
import requests
from collections import Counter
from django.http import JsonResponse
from spotipy.oauth2 import SpotifyOAuth

lemmatizer = WordNetLemmatizer()

def home(request):
    return render(request,"index.html",{})

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


def chat(request):
    msg = request.GET.get('user_message')
    msg1=msg.lower()
    response = chatbot_response(msg1)
    Conversation.objects.create(user_input=msg, response=response) 
    return JsonResponse({'response':response})

def analyze_emotion(request):
    latest_five_conversations = Conversation.objects.order_by('-id')[:5]
    total_emotions = Counter()
    for conversation in latest_five_conversations:
        msg = conversation.user_input
        emotions = te.get_emotion(msg)
        if emotions:
            total_emotions.update(emotions)
        else:
            continue

    if not total_emotions:  # Check if there are any emotions aggregated
        return JsonResponse({'error': 'No valid emotions found from the last 5 messages'}, status=400)
    max_emotion = total_emotions.most_common(1)[0][0]
    emotion_label = emotion_labels.get(max_emotion, 'unknown')
    Emotion.objects.create(emotion=emotion_label)
    return JsonResponse({'emotion': emotion_label}, status=200)


CLIENT_ID = '5f23245341574c4f8197d92d339cb2e7'
CLIENT_SECRET = 'ca3bf1d79a8f48b9be4a50574c18adb8'
REDIRECT_URI = 'http://localhost:8000/callback'

def login(request):
    scope = 'user-read-private user-read-email'
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope}"
    return redirect(auth_url)

def callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Authorization code not provided'}, status=400)

    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to retrieve access token'}, status=response.status_code)

    token_info = response.json()
    access_token = token_info.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'Access token not found'}, status=500)

    # Store the access token in the session if needed
    request.session['access_token'] = access_token
    return redirect('index')  # Redirect to the index page after login