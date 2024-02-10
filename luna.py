import pyttsx3
import pyaudio
import speech_recognition as sr
import wikipedia as wk
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from heapq import nlargest

nltk.download('punkt')
nltk.download('stopwords')

def summarize_text(text, num_sentences=3):
    # Tokenizzazione del testo in frasi
    sentences = sent_tokenize(text)

    # Tokenizzazione delle parole e rimozione delle stopwords
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    # Calcolo della frequenza delle parole
    word_freq = nltk.FreqDist(words)

    # Assegnazione di un peso alle frasi
    sentence_scores = {}
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_freq:
                if len(sentence.split(' ')) < 30:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_freq[word]
                    else:
                        sentence_scores[sentence] += word_freq[word]

    # Selezione delle frasi più significative
    summarized_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summarized_sentences)
    return summary

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

def search_wikipedia(query):
    try:
        search_results = wk.search(query)

        if search_results:
            page = wk.page(search_results[0])
            
            return page.content
        else:
            return "I'm sorry, I haven't found any result on wikipedia for your request"
    except wk.exceptions.DisambiguationError as e:
        return "There are too many articles about your request, can you give me more details?"
    except wk.exceptions.PageError as e:
        return "Sorry, I haven't found anything for your request"

commonSearchWikipedias = open('commonSearchRequest.json', 'r')
commonSearchPhrases = json.load(commonSearchWikipedias)["search_phrases"]
print(commonSearchPhrases)

engine = pyttsx3.init(driverName='sapi5')

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3].id) 

micRec = sr.Recognizer()

with sr.Microphone() as source:
    engine.say("Hi Giovanni, how are you doing? How can I help you today?")
    audio = micRec.listen(source)
try:
    userRequest = micRec.recognize_google(audio, language="en-EN").lower()
    if string_contains_any_searchrequest(userRequest, commonSearchPhrases):
        wikiResearch = exclude_strings(userRequest, commonSearchPhrases, "on wikipedia")
        print("I'm searching " + wikiResearch + " on wikipedia for you")
        searchResult = search_wikipedia(wikiResearch)
        print(wk.summary(searchResult)) #fixare il summarize, magari lavorando con le sezioni del risultato
        
        
except sr.UnknownValueError:
    engine.say("I haven't understand what you said, can you repeat?")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

engine.runAndWait()
