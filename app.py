from flask import (
    Flask,
    request,
    url_for
    )
from helper import vibconnect
from tiniyo.voice_response import VoiceResponse
from config import *

app = Flask(__name__)


@app.route("/")
def hello():
    return "HELLO WORLD to see the IVR DEMO go to https://ivr-python.herokuapp.com/welcome"

@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
      response = VoiceResponse()
      with response.gather(
        num_digits=1, voice="alice", language="en-IN", action=url_for('welcomeCB',_scheme='http',_external=True), method="POST"
         
      ) as g:
        g.say(message="Thanks for calling Vibconnect. IVR Phone Home Service. " +
              " Please press 1 for Table reservation." +
              " Press 2 for your loyality point." +
              " Press 3 for any other query.")
        
      return vibconnect(response)

# @app.route("/welcome", methods=['GET', 'POST'])
# def play():

#      response = VoiceResponse()
#      response.play("http://vibconnect.io/vibconnect/intro-vibtree.mp3",action=url_for('receptionCB',_scheme='http',_external=True), method="POST")
#      return vibconnect(response)

@app.route("/test")
def test():
    response = VoiceResponse()
    response.dial("917596035307")
    return vibconnect(response)

@app.route('/welcomeCB', methods=['POST'])
def welcomeCB():
    app.logger.error("DTMFGathertime response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    #selected_option = request.form['Digits']
    app.logger.error("welcomeCB digit received = %s" % selected_option)
    option_actions = {'1': "tablebooking",
                      '2': "loyalitypoint",
                      '3': "otherquery",
                      '0': "listenagain"
                    #   'null':"goBackToWelcome"
                      }

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = _tablereservation()
            return vibconnect(response)
        elif int(selected_option) == 2:
            response = _loyality_point(request.json.get('From'))
            return vibconnect(response)
        elif int(selected_option) == 3:
            response = _forotherquery()
            return vibconnect(response)
        elif int(selected_option == 0):
            response = _redirect_welcome()
            return vibconnect(response)
    else:
        return _redirect_welcome()

def _tablereservation():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('reservation_day',_scheme='http',_external=True), method="POST"
    ) as g:

        g.say("Press 1 for today " +
              "Press 2 for tomorrow " +
              "To go back to the main menu " +
              " press the star key.",
              voice="alice", language="en-GB", loop=3)

    return response

def _redirect_welcome():
    response = VoiceResponse()
    response.say(message="you entered a wrong input",action=url_for('welcomeCB',_scheme='http',_external=True), method='POST')
    

    return response

def _loyality_point(customer_number):
    response = VoiceResponse()
    req_body = {'customer_key': customer_key, 'merchant_id': merchant_id, 'customer_mobile': customer_number}
    my_headers = {'x-api-key' : x_api_key,'Content-Type':'application/json','Accept':'application/json'}
    custresp = requests.get(customer_check_url,headers=my_headers,json=req_body)
    if (response.status_code == 200):
        response.say("Your loyality points are "+response.json().response.details.currentpoints,voice="alice", language="en-GB")
        # Code here will only run if the request is successful
    else:
        response.say("To get to _loyality_point, please visit our website",voice="alice", language="en-IN")
    response.hangup()
    return response


def _tableservationtime_today():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('tableservationtimetoday',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-IN", loop=3)
    return response

def _tableservationtime_tomorrow():
    response = VoiceResponse()
    with response.gather(
        numDigits=1, action=url_for('tableservationtimetomorrow',_scheme='http',_external=True), method="POST"
    ) as g:
        g.say("Press 1 for breakfast, press 2 for lunch, press 3 for dinner" ,voice="alice", language="en-IN", loop=3)
    return response


def _forotherquery():
    response = VoiceResponse()
    response.dial(reception_number,timeout=30,action=url_for('receptionCB',_scheme='http',_external=True), method="POST")
    return response



@app.route('/receptionCB', methods=['GET','POST'])
def receptionCB():
    response = VoiceResponse()
    response.dial(manager_number, timeout=30,action=url_for('managerCB',_scheme='http',_external=True), method="POST")
    # return response
    return vibconnect(response)



@app.route('/managerCB', methods=['GET','POST'])
def managerCB():
    response = VoiceResponse()
    response.dial(owner_number, timeout=30,action=url_for('ownerCB',_scheme='http',_external=True), method="POST")
    return vibconnect(response)

@app.route('/ownerCB', methods=['GET','POST'])
def ownerCB():
    response = VoiceResponse()
    response.dial(owner_number, timeout=30,action=url_for('ownerCB',_scheme='http',_external=True), method="POST")
    # response.say(message="thanks for calling owner")
    return vibconnect(response)

    

if __name__=="__main__":
    app.run(debug=True)