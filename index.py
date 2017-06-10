# -*- coding: utf-8 -*-

from __future__ import print_function
import duckduckgo
import re

s3_bucket  = "https://s3-eu-west-1.amazonaws.com/alexa-enteente/"
img_small  = s3_bucket + "sketch-756.png"
img_large  = s3_bucket + "sketch-1280.png"
myname     = 'Nak-Nak-Nak'
lang       = ''

br = "\n\n"

def lambda_handler(event, context):

    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    tmp = event['request']['locale']
    tmp = tmp.split('-')
    lang = tmp[0]

    print('lang: ' + lang)

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'], lang)
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'], lang)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session, lang):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_hello_response(lang)


def on_intent(intent_request, session, lang):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "searchDuckIntent":
        return searchDuck(intent, session, lang)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(lang)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response(lang):
    session_attributes = {}
    myname = 'Nak-Nak-Nak'
    if lang == 'de':
        speech_output = "Ich kann deine Frage an Dack Dack Go richten, eine freie Suchmaschine. " \
                    + br + "Sie sammelt oder teilt keine personenbezogenen Daten. " \
                    + br + br + "Stell mir eine Frage, und ich liefere dir Suchergebnisse und Informationen."
        reprompt_text = "Du kannst mich alles fragen wie zum Beispiel: Wer sind die Simpsons?"
        card_text = speech_output.replace( "Dack Dack Go", "DuckDuckGo")
    elif lang == 'en':
        speech_output = "I can look up your questions on Duck Duck Go, a free search engine. " \
                    + br + "It does not collect or share personal information. " \
                    + br + br + "Give me something to look up, and I'll return search results and info."
        reprompt_text = "You can ask me something like, What is Python?"
        myname = 'Quack-Quack'
        card_text = speech_output.replace( "Duck Duck Go", "DuckDuckGo")
    card_title = myname

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, card_text, None))

def get_hello_response(lang):
    session_attributes = {}
    speech_output = 'Ask me'
    reprompt_text = 'reprompt'
    if lang == 'de':
        speech_output = 'Willkommen bei Naak-Naak-Naak. Frag mich irgendwas!'
        reprompt_text = 'Du kannst mich alles fragen wie zum Beispiel: Wer sind die Simpsons?'
    elif lang == 'en':
        speech_output = 'Welcome to Quack-Quack. Ask me something!'
        reprompt_text = 'You can ask me something like, What is Python?'
    card_title = None

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, speech_output, None))


def handle_session_end_request():
    should_end_session = True
    return build_response({}, build_speechlet_response(
        None, None, None, should_end_session, None, None))


def format_url(s, lang='en', all=False):
    if not s:
        ret = ''
    else:
        if all:
            s = s.replace('https://', '')
            s = s.replace('http://',  '')
            src = 'forward u r l : '
            slash = ' slash '
            if lang == 'de':
                src = 'Weiterleitungs-U R L : '
                slash = ' Släsch '
            s = s.replace('/',  slash)
        else:
            s = re.split('/', s)
            s = s[2]
            src = 'source: '
            if lang == 'de':
                src = 'Quelle: '
        dot = ' dot '
        if lang == 'de':
            dot = ' Punkt '
        s = s.replace("www.", "")
        s = s.replace(".", dot)
        s = s.replace(" de", " d.e.")
        s = s.replace("de ", "d.e. ")
        s = s.replace(" uk", " u.k.")
        s = s.replace("uk ", "u.k. ")
        s = s.replace(" fr", " f.r.")
        s = s.replace(" io", " i.o.")
        ret = br + src + s
    return ret

def searchDuck(intent, session, lang='en'):
    card_img = None
    card_text = None
    card_title = None
    lookupString = ''
    reprompt_text = ""
    should_end_session = True
    speech_output = ''
    if 'query' in intent['slots']:
        if 'value' in intent['slots']['query']:
            lookupString = intent['slots']['query']['value']
    else:
        speech_output = 'Sorry, I didn\'t understand'
        if lang == 'de':
            speech_output = 'Sorry, das habe ich nicht verstanden'
        elif lang == 'en':
            speech_output = 'I\'m sorry, I didn\'t understand, you can say something like: Who is Tycho the musician?'

        return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session, None, None))

    #Gets the First Result of a DuckDuckGo
    try:
        queryRun, card_img, url = duckduckgo.get_zci(lookupString, lang, True)
    except ValueError:
        if lang == 'de':
            speech_output = "Es gab ein Problem beim erreichen von Dack Dack Go, versuche es später nochmal"
            card_text = speech_output.replace( "Dack Dack Go", "DuckDuckGo")
        elif lang == 'en':
            speech_output = "There was a problem contacting DuckDuckGo, could you try a little later?"
            card_text = speech_output

        return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session, card_text, None))
    else:
        queryRun = queryRun.encode('utf-8')
        print("queryRun: " + queryRun)
        print("url: " + url)
        if queryRun.find('http') == 0:
            speech_output = format_url(queryRun, lang, True)
            card_text = queryRun
            card_title = 'see this URL'
            if lang == 'de':
                card_title = 'Siehe hier'
        elif queryRun == '-no-results-':
            if not url:
                speech_output = 'leider wurde nichts gefunden. Versuchs noch mal!'
                reprompt_text = "Versuche eine andere Formulierung. Sage Stopp zum Beenden"
                if lang == 'en':
                    speech_output = 'nothing found. Try again!'
                    reprompt_text = 'Formulate your question different. Say "stop" to leave'
                should_end_session = False
            else:
                speech_output = url
        else:
            speech_output = queryRun + format_url(url, lang, False)

        if card_img:
            card_title = lookupString
            card_text = queryRun
            speech_output += br + 'Ich schicke eine Karte in die Alexa App.'

        return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session, card_text, card_img))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, card_text, card_img):
    if output == None:
        return {
            'shouldEndSession': should_end_session
        }
    elif title == None:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }
    else:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Standard',
                'title':  title,
                'image': {
                    'smallImageUrl': img_small,
                    'largeImageUrl': img_large
                },
                'text': card_text
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
