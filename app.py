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
              " Press 3 for any other query."+
              " Press 0 for listen again."+
              "                          ")
        
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
        elif int(selected_option)==0 :
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
    custresp = request.get(customer_check_url,headers=my_headers,json=req_body)
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

@app.route('/tableservationtimetomorrow', methods=['POST'])
def tableservationtimetomorrow():
    #selected_option = request.form['Digits']
    app.logger.error("tableservationtimetomorrow response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("tableservationtimetomorrow digit received = %s" % selected_option)
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}

    print("Table is booked for tomorrow for %s" % option_actions[selected_option])
    ###SEND SMS https://github.com/tiniyo/tiniyo-python
    return _redirect_confirmation("Tomorrow "+option_actions[selected_option], request.form.get("From"))

@app.route('/tableservationtimetoday', methods=['POST'])
def tableservationtimetoday():
    app.logger.error("tableservationtimetoday response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("tableservationtimetoday digit received = %s" % selected_option)
    option_actions = {'1': "breakfast",
                      '2': "lunch",
                      '3': "dinner"}
    print("Table is booked for today for %s" % option_actions[selected_option])
    ###SEND SMS https://github.com/tiniyo/tiniyo-python
    return _redirect_confirmation("Today "+option_actions[selected_option], request.form.get("From"))


@app.route('/reservation_day', methods=['POST'])
def reservation_day():
    app.logger.error("reservation_day response = %s" % request.get_json())
    digit = None
    if request.get_json() is not None:
        if 'Digits' in request.get_json():
            selected_option = request.json.get('Digits')
    # selected_option = request.form['Digits']
    app.logger.error("reservation_day digit received = %s" % selected_option)
    option_actions = {'1': "today",
                      '2': "tomorrow",
                      '*': "welcome"}

    if selected_option in option_actions:
        if int(selected_option) == 1:
            response = _tableservationtime_today()
            return vibconnect(response)
        elif int(selected_option) == 2:
            response = _tableservationtime_tomorrow()
            return vibconnect(response)
    return _redirect_welcome()

def _redirect_confirmation(time, customer_number):
    response = VoiceResponse()
    response.say("Your reservation is successfully booked for "+time+". You will received sms shortly", voice="alice", language="en-GB")
    response.say("Good Bye", voice="alice", language="en-GB")
    
    # client = Client(auth_id, auth_secret)
    # # Send SMS to customer of confirmation. 
    # message = client.messages.create(
    #                           body="Your reservation is successfully booked for "+ time +".",
    #                           from_=sender_id,
    #                           to=customer_number
    #                       )
    return vibconnect(response)



if __name__=="__main__":
    app.run(debug=True)