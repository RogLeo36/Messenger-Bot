"""
Simple Facebook Echo bot: Respond with exactly what it receives
Standalone version
"""

import sys, json, traceback, requests
from flask import Flask, request

application = Flask(__name__)
app = application
PAT = 'EAAqZCCHcyVggBAGnQA5CxxRsQLDzSZBDi2MskESYH3SWNdMQVZAIZC3ZCLaeW21YjQNd3UPKU5E0uriyZCPP2YuIEKKVadfwx6dZCaZA3oU4umHMSmHEYfx61jkJZAoTGPAJsuiVGZARbZBu2XP1a7WwgKqV4qa2egQpkiY27tyofWP7QZDZD'
VERIFICATION_TOKEN = 'asdfghjkl'
SEND_API_URL = 'https://graph.facebook.com/v2.12/me/messages?access_token=%s'\
  % PAT
@app.route('/', methods=['GET'])
def handle_verification():
    print ("Handling Verification.")
    if request.args.get('hub.verify_token', '') == VERIFICATION_TOKEN:
        print ("Webhook verified!")
        return request.args.get('hub.challenge', '')
    else:
        return "Wrong verification token!"

# ======================= Bot processing ===========================
@app.route('/', methods=['POST'])
def handle_messages():
    body = json.loads(request.data)

    try:
    for entry in body['entry']:
        if 'messaging' in entry:
          for message in entry['messaging']:
            sender = message['sender']['id']
            if 'message' in message and 'is_echo' in message['message']:
              return 
            if 'message' not in message and 'postback' not in message:
              return 
            print('sender1111')
            send_message_to_recipient(json.dumps(body), sender)
            print('sender')
            print(sender)
            return
        if 'standby' in entry:
          for message in entry['standby']:
            sender = message['sender']['id']
            if 'message' in message and 'is_echo' in message['message']:
              return 
            if 'message' not in message and 'postback' not in message:
              return 
            print('sender1111')
            send_message_to_recipient(json.dumps(body), sender)
            print('sender')
            print(sender)
            return
            
    print('sender')
  except Exception as e:
     print("swapnilc-Exception sending")
     print(e)

def processIncoming(user_id, message):
    if message['type'] == 'text':
        message_text = message['data']
        return message_text

    elif message['type'] == 'location':
        response = "I've received location (%s,%s) (y)"%(message['data'][0],message['data'][1])
        return response

    elif message['type'] == 'audio':
        audio_url = message['data']
        return "I've received audio %s"%(audio_url)

    # Unrecognizable incoming, remove context and reset all data to start afresh
    else:
        return "*scratch my head*"


def send_message(token, user_id, text):
    """Send the message text to recipient with id recipient.
    """
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": user_id},
                          "message": {"text": text.decode('unicode_escape')}
                      }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print (r.text)

# Generate tuples of (sender_id, message_text) from the provided payload.
# This part technically clean up received data to pass only meaningful data to processIncoming() function
def messaging_events(payload):
    
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    
    for event in messaging_events:
        sender_id = event["sender"]["id"]

        # Not a message
        if "message" not in event:
            yield sender_id, None

        # Pure text message
        if "message" in event and "text" in event["message"] and "quick_reply" not in event["message"]:
            data = event["message"]["text"].encode('unicode_escape')
            yield sender_id, {'type':'text', 'data': data, 'message_id': event['message']['mid']}

        # Message with attachment (location, audio, photo, file, etc)
        elif "attachments" in event["message"]:

            # Location 
            if "location" == event['message']['attachments'][0]["type"]:
                coordinates = event['message']['attachments'][
                    0]['payload']['coordinates']
                latitude = coordinates['lat']
                longitude = coordinates['long']

                yield sender_id, {'type':'location','data':[latitude, longitude],'message_id': event['message']['mid']}

            # Audio
            elif "audio" == event['message']['attachments'][0]["type"]:
                audio_url = event['message'][
                    'attachments'][0]['payload']['url']
                yield sender_id, {'type':'audio','data': audio_url, 'message_id': event['message']['mid']}
            
            else:
                yield sender_id, {'type':'text','data':"I don't understand this", 'message_id': event['message']['mid']}
        
        # Quick reply message type
        elif "quick_reply" in event["message"]:
            data = event["message"]["quick_reply"]["payload"]
            yield sender_id, {'type':'quick_reply','data': data, 'message_id': event['message']['mid']}
        
        else:
            yield sender_id, {'type':'text','data':"I don't understand this", 'message_id': event['message']['mid']}

def send_message_to_recipient(message_text, recipient_id):
  message = {
    'recipient': {
      'id': recipient_id,
    },
    'message': {
      'text': message_text,
    },
  }
  r = requests.post(SEND_API_URL, data=json.dumps(message), headers=HEADERS)
  if r.status_code != 200:
    print('====ERROR====')
    print(r.json())
    print('==============')

# Allows running with simple `python <filename> <port>`
if __name__ == '__main__':
    if len(sys.argv) == 2: # Allow running on customized ports
        app.run(port=int(sys.argv[1]))
    else:
        app.run() # Default port 5000