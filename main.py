from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import keyboard

import openai

# Load credentials
import os
from dotenv import load_dotenv
load_dotenv()

# Google TTS
import google.cloud.texttospeech as tts
import pygame
import time

# Mute ALSA errors...
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    try: 
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        print('')

### PARAMETERS ###
activationWords = ['computer', 'calcutron', 'shodan', 'showdown']
tts_type = 'local' # google or local

# Local speech engine initialisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0 = male, 1 = female

# Google TTS client
def google_text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])

    # Set the text input to be synthesized
    text_input = tts.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the voice name
    voice_params = tts.VoiceSelectionParams(
        language_code=en-IN, name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    return response.audio_content

# Configure browser
# Set the path
firefox_path = r"usr/bin/firefox"#use chrome at place of fire fox also down
# Register the browser
webbrowser.register('firefox', None, 
                    webbrowser.BackgroundBrowser(firefox_path))

# Wolfram Alpha client
appId = '5R49J7-J888YX9J2V'
wolframClient = wolframalpha.Client(appId)

def speak(text, rate = 120):
    time.sleep(0.3)
    try:     
        if tts_type == 'local':
            engine.setProperty('rate', rate) 
            engine.say(text, 'txt')
            engine.runAndWait()
        if tts_type == 'google':
            speech = google_text_to_wav('en-US-News-K', text)
            pygame.mixer.init(frequency=12000, buffer = 512)
            speech_sound = pygame.mixer.Sound(speech)
            speech_length = int(math.ceil(pygame.mixer.Sound.get_length(speech_sound)))
            speech_sound.play()
            time.sleep(speech_length)
            pygame.mixer.quit()
 
    ## The standard keyboard interrupt is Ctrl+C. This interrupts the Google speech synthesis.
    except KeyboardInterrupt:
        try:
            if tts_type == 'google':
                pygame.mixer.quit()
        except:
            pass
        return


def parseCommand():
    with noalsaerr():
        listener = sr.Recognizer()
        print('Listening for a command')

        with sr.Microphone() as source:
            listener.pause_threshold = 2
            input_speech = listener.listen(source)

        try:
            print('Recognizing speech...')
            query = listener.recognize_google(input_speech, language='en_IN')
            print(f'The input speech was: {query}')

        except Exception as exception:
            print('I did not quite catch that')
            print(exception)

            return 'None'

        return query

def search_wikipedia(keyword=''):
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0]) 
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframalpha(keyword=''):
    response = wolframClient.query(keyword)
  
    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods

    # Query not resolved
    if response['@success'] == 'false':
        speak('sorry not abel to compute')
    # Query resolved
    else: 
        result = ''
        # Question
        pod0 = response['pod'][0]
        # May contain answer (Has highest confidence value) 
        # if it's primary or has the title of result or definition, then it's the official result
        pod1 = response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove bracketed section
            return result.split('(')[0]
        else:
            # Get the interpretation from pod0
            question = listOrDict(pod0['subpod'])
            # Remove bracketed section
            question = question.split('(')[0]
            # Could search wiki instead here? 
            return question

'''def query_openai(prompt = ""):
    openai.organization = os.environ['OPENAI_ORG']
    openai.api_key = os.environ['OPENAI_API_KEY']'''
chatStr = ""
# https://youtu.be/Z3ZAJoi4x6Q
def chat(query):
    global chatStr
    print(chatStr)
    openai.api_key = apikey
    chatStr += f"kamal: {query}\n Jarvis: "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= chatStr,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # todo: Wrap this inside of a  try catch block
    say(response["choices"][0]["text"])
    chatStr += f"{response['choices'][0]['text']}\n"
    return response["choices"][0]["text"]


def ai(prompt):
    openai.api_key = apikey
    text = f"OpenAI response for Prompt: {prompt} \n *************************\n\n"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # todo: Wrap this inside of a  try catch block
    # print(response["choices"][0]["text"])
    text += response["choices"][0]["text"]
    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    # with open(f"Openai/prompt- {random.randint(1, 2343434356)}", "w") as f:
    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip() }.txt", "w") as f:
        f.write(text)


    # Temperature is a measure of randonmess
    # Max_tokens is the number of tokens to generate
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=80,

    )

    return response.choices[0].text

# Main loop
if __name__ == '__main__': 
    speak('All systems nominal.', 120)

    while True:
        # Parse as a list
        # query = 'computer say hello'.split()
        query = parseCommand().lower().split()

        if query[0] in activationWords and len(query) > 1:
            query.pop(0)

            # Set commands
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, all!')
                else:
                    query.pop(0) # Remove 'say'
                    speech = ' '.join(query) 
                    speak(speech)

            # Query OpenAI
            if query[0] == 'insight':
                query.pop(0) # Remove 'insight'
                query = ' '.join(query)
                speech = query_openai(query)
                speak("Ok")
                speak(speech)

            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening... ')
                # Assume the structure is activation word + go to, so let's remove the next two words
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)

            # Wikipedia
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Querying the universal databank')
                time.sleep(2)
                speak(search_wikipedia(query))

            # Wolfram Alpha
            if query[0] == 'find' or query[0] == 'computer':
                query = ' '.join(query[1:])
                try:
                    result = search_wolframalpha(query)
                    speak(result)
                except:
                    speak('Unable to compute')

            # Note taking
            if query[0] == 'log':# speak this and computer start taking notes
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(now)
                    newFile.write(' ')
                    newFile.write(newNote)
                speak('Note written')

            if query[0] == 'sleep':#its stop
                speak('Goodbye')
                break
while True:
        print("Listening...")
        query = takeCommand()
        # todo: Add more sites
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"], ["google", "https://www.google.com"],]
        for site in sites:
            if f"Open {site[0]}".lower() in query.lower():
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])

if "open music" in query:
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            os.system(f"open {musicPath}")

        elif "the time" in query:
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            say(f"Sir time is {hour} bajke {min} minutes")

        elif "open facetime".lower() in query.lower():
            os.system(f"open /System/Applications/FaceTime.app")

        elif "open pass".lower() in query.lower():
            os.system(f"open /Applications/Passky.app")

        elif "Using artificial intelligence".lower() in query.lower():
            ai(prompt=query)

        elif "Jarvis Quit".lower() in query.lower():
            exit()

        elif "reset chat".lower() in query.lower():
            chatStr = ""

        else:
            print("Chatting...")
            chat(query)