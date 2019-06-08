from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from utils import fetch_reply
GOOD_BOY_URL = "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"
@app.route("/sms", methods=['POST','GET'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(request.form)
    msg = request.form.get('Body')
    sender = request.form.get('From')
    if(msg==""):    # when media was send, message space was empty to cover it 
        msg="Random image"
    # Create reply
    resp = MessagingResponse()
    
    text,reply=fetch_reply(msg,sender)
    if text=='picture':
        resp.message(reply).media(reply)
    elif text=='image_whatsapp':
        num_media = int(request.values.get("NumMedia"))
        
        if not num_media:
            msg = resp.message("Send us an image!")
        else:
            msg = resp.message("Thanks for the image(s).")
            msg.media(GOOD_BOY_URL)
    else:
        resp.message(reply)
    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

