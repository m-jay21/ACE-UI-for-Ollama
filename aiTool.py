import subprocess
import re
import time
import sys
import ollama
import json


def aiOptions():
    response = ollama.list()

    model_names = [model.model for model in response.models]
    return(model_names)

def cleanAnsi(text):
    #removes any ansi characters and spinning values that ollama outputs
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    spinner_artifacts = re.compile(r'[⠋⠙⠹⠼⠧⠇⠏⠸⠴⠦⠬⠰⠾⠶⠖⠆⠖⠲]+')
    text = ansi_escape.sub('', text)
    text = spinner_artifacts.sub('', text)
    #keeps a space after punctuation if needed.
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    return text

def downloadModel(text):
    if text in aiOptions():
        return "Already Installed"
    try:
        ollama.pull(text)
    except Exception as e:
        return "Cannot be installed"
    
    return "Installed"

def runData(text, model):
    #append user message
    with open("theMessages.txt", 'a') as file:
        file.write(json.dumps({"role": "user", "content": text}) + "\n")

    #open the file for reading
    with open("theMessages.txt", 'r') as file:
        lines = file.readlines() 
        theMessages = [json.loads(line.strip()) for line in lines if line.strip()]  #convert JSON strings to dicts

    #send messages to Ollama
    stream = ollama.chat(model=model, messages=theMessages, stream=True)

    full_response = ""

    for chunk in stream:
        word = chunk.get('message', {}).get('content', '')
        full_response += word
        yield word  #yield word-by-word

    #append assistant response properly
    with open("theMessages.txt", 'a') as file:
        file.write(json.dumps({"role": "assistant", "content": full_response}) + "\n")