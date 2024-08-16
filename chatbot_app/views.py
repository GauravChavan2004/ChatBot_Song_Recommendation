import nltk
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
import spacy
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .models import Conversation
from .intent_data import intents

def home(request):
    return render(request,"index.html")

nlp = spacy.load("en_core_web_sm")

def process_input(request):
    user_input = request.GET.get("userMessage")
    tokens = word_tokenize(user_input)
    doc = nlp(" ".join(tokens))
    intent = None
    for entity in doc.ents:
        for intent_data in intents["intents"]:
            if entity.text.lower() in [pattern.lower() for pattern in intent_data["patterns"]]:
                intent = intent_data["tag"]
                break
        if intent:
            break
    if intent:
        response = next(intent_data["response"] for intent_data in intents["intents"] if intent_data["tag"] == intent)
       
    else:
        response = "I didn't understand that. Please try again."
    Conversation.objects.create(user_input=user_input, response=response)
    return HttpResponse({"response": response})
    