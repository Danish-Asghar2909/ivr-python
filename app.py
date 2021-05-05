from flask import (
    Flask,
    request,
    url_for
    )
from helper import tiniyoml
from tiniyo.voice_response import VoiceResponse
from config import *

app = Flask(__name__)


@app.route("/")
def hello():
    return "HELLO WORLD to see the IVR DEMO go to http://127.0.1:5000/welcome"

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
      response = VoiceResponse()
      with response.gather(
        num_digits=1, action=url_for('welcome',_scheme='http',_external=True), method="POST"
      ) as g:
        g.say(message="Thanks for calling Vibconnect IVR Phone Home Service. " +
              "Please press 1 for Table reservation." +
              "Press 2 for your loyality point." +
              "Press 2 for any other query.", loop=3)
        g.say(message="please press the correct number")
      return tiniyoml(response)

@app.route("/test")
def test():
    response = VoiceResponse()
    response.dial("8240182045")
    return tiniyoml(response)


    

if __name__=="__main__":
    app.run(debug=True)