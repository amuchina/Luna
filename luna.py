import pyttsx3
import speech_recognition as sr
import wikipedia as wk
import json

# Funzione per controllare se una stringa contiene una delle frasi di ricerca comuni
def string_contains_any_searchrequest(string, searchPhrases):
    for element in searchPhrases:
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

# Carica le frasi di ricerca comuni da un file JSON
commonSearchPhrasesFile = open('commonSearchRequest.json', 'r')
commonSearchPhrases = json.load(commonSearchPhrasesFile)["search_phrases"]

# Inizializza il motore TTS con la lingua inglese
engine = pyttsx3.init(driverName='sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)  # Seleziona una voce in inglese

# Inizializza il recognizer per l'ascolto con la lingua inglese
micRec = sr.Recognizer()

# Saluta l'utente all'inizio
engine.say("Hey Giovanni! How can I assist you today?")
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
        if string_contains_any_searchrequest(userRequest, commonSearchPhrases):
            # Esegui la ricerca su Wikipedia
            wikiResearch = exclude_strings(userRequest, commonSearchPhrases, "on wikipedia")
            engine.say("I'm searching " + wikiResearch + " on Wikipedia for you.")
            searchResult = search_wikipedia(wikiResearch)
            engine.say(searchResult)  # Lettura del riassunto dal risultato di Wikipedia
        elif userRequest == 'no' or userRequest == 'nothing':
            engine.say("Okay, have a great day!")
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
    engine.say("Is there anything else I can assist you with?")
    engine.runAndWait()
