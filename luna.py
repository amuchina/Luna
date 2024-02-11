import pyttsx3
import speech_recognition as sr
import wikipedia as wk
import pyjokes as pj
import json
from dotenv import load_dotenv, dotenv_values, set_key
import os
import random

envPath = '.env'
load_dotenv(envPath)

# Funzione per controllare se una stringa contiene una delle frasi di ricerca comuni
def string_contains_any_request(string, phrases):
    for element in phrases:
        if element in string:
            return True
    return False

def exclude_strings(string, exclude_list, *additional_exclusions):
    exclusions = set(exclude_list + list(additional_exclusions))
    for item in exclusions:
        string = string.replace(item, "")
    return string

# Funzione per eseguire una ricerca su Wikipedia
def search_wikipedia(query):
    try:
        search_results = wk.search(query)

        if search_results:
            page = wk.page(search_results[0])
            return page.summary
        else:
            return "I'm sorry, I haven't found any result on Wikipedia for your request"
    except wk.exceptions.DisambiguationError as e:
        return "There are too many articles about your request, can you give me more details?"
    except wk.exceptions.PageError as e:
        return "Sorry, I haven't found anything for your request"
    
def tell_joke():
    joke = pj.get_joke()
    return joke

# Carica le frasi di ricerca comuni da un file JSON
commonSearchPhrasesFile = open('commonSearchRequest.json', 'r')
commonSearchPhrases = json.load(commonSearchPhrasesFile)["search_phrases"]

commonUpdateProfilePhrasesFile = open('commonUpdateProfileRequest.json', 'r')
commonUpdateProfilePhrases = json.load(commonUpdateProfilePhrasesFile)["modify_info_phrases"]

commonJokesRequestFile = open('commonJokesRequest.json', 'r')
commonJokesRequestPhrases = json.load(commonJokesRequestFile)["joke_request_phrases"]

commonNeedMoreRequestFile = open('commonNeedMoreRequest.json', 'r')
commonNeedMoreRequestPhrases = json.load(commonNeedMoreRequestFile)["need_more_phrases"]

# Inizializza il motore TTS con la lingua inglese
engine = pyttsx3.init(driverName='sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)  # Seleziona una voce in inglese

# Inizializza il recognizer per l'ascolto con la lingua inglese
micRec = sr.Recognizer()

# Saluta l'utente all'inizio
engine.say(f"Hey {os.getenv("USER_FIRST_NAME")}! How can I assist you today?")
engine.runAndWait()

# Loop di conversazione
while True:
    # Ascolta l'input dell'utente
    with sr.Microphone() as source:
        audio = micRec.listen(source)
    
    try:
        # Trascrivi l'input dell'utente
        userRequest = micRec.recognize_google(audio, language="en-EN").lower()
        
        # Elabora la richiesta solo se contiene una delle frasi di ricerca comuni
        if string_contains_any_request(userRequest, commonSearchPhrases):
            # Esegui la ricerca su Wikipedia
            wikiResearch = exclude_strings(userRequest, commonSearchPhrases, "on wikipedia")
            engine.say("I'm searching " + wikiResearch + " on Wikipedia for you.")
            searchResult = search_wikipedia(wikiResearch)
            engine.say(searchResult)  # Lettura del riassunto dal risultato di Wikipedia
        elif string_contains_any_request(userRequest, commonUpdateProfilePhrases): #da fixare, dopo aver chiesto quale informazione si vuole aggiornare triggera subito "richiesta non capita"
            engine.say("What information would you like to update? First name, last name, age, nickname or residence?")
            with sr.Microphone() as source:
                audio = micRec.listen(source)
            try:
                userRequest = micRec.recognize_google(audio, language="en-EN").lower()

                if userRequest == 'first name':
                    engine.say("Ok, what is your first name?")
                    with sr.Microphone() as source:
                        audio = micRec.listen(source)
                    try:
                        userRequest = micRec.recognize_google(audio, language="en-EN").lower()
                        set_key(envPath, 'USER_FIRST_NAME', userRequest)
                    except sr.UnknownValueError:
                        engine.say("Sorry, I didn't understand your request")
                    except sr.RequestError as e:
                        engine.say("Could not request results from Google Speech Recognition service; {0}".format(e))

                    engine.say("Ok, from now on I will remember your first name is " + os.getenv("USER_FIRST_NAME"))

            except sr.UnknownValueError:
                engine.say("Sorry, I didn't understand your request")
            except sr.RequestError as e:
                engine.say("Could not request results from Google Speech Recognition service; {0}".format(e))
        elif string_contains_any_request(userRequest, commonJokesRequestPhrases):
            engine.say("Ok, here's a joke")
            engine.say(tell_joke())
        elif userRequest == 'nothing':
            engine.say("Okay, have a great day! I'm here if you need help!")
            engine.runAndWait()
            break
        else:
            engine.say("I'm sorry, I didn't understand your request.")
        
        engine.runAndWait()  # Attendere che l'assistente finisca di parlare

    except sr.UnknownValueError:
        engine.say("I didn't catch that, could you please repeat?")
        engine.runAndWait()
    except sr.RequestError as e:
        engine.say("Could not request results from Google Speech Recognition service; {0}".format(e))

    # Chiedi all'utente se c'è bisogno di altro
    engine.say(random.choice(commonNeedMoreRequestPhrases))
    engine.runAndWait()