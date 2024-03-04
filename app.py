from flask import Flask, request, jsonify
from pymongo import MongoClient
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
load_dotenv('.env')


app = Flask(__name__)

# MongoDB connection.
#client = MongoClient('mongodb+srv://11230316a:Kungu.maitu3@cluster0.sc7s21e.mongodb.net/')
uri = os.getenv('URI')
client = MongoClient(URI, server_api=ServerApi('1'))db = client.EABL2
Liqour_collection = db.LIQOUR
###########################################
global the_response 

#Twilio intergration:
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
#############################################



@app.route('/Liqour', methods=['GET'])
def get_Liqour():
    projection = {'Brand': 1, 'Category': 1, 'Package': 1, 'ABV': 1, '_id': 0}
    Liqour = list(Liqour_collection.find({}, projection))

    for liquor in Liqour:
        if '_id' in liquor:
            liquor['_id'] = str(liquor['_id'])

    return jsonify({'Liqour': Liqour})


@app.route('/Verification-code', methods=['GET', 'POST'])
def get_VerificationCode():
    #customer_code = "5389XPIF1198"
    incoming_message = request.form['Body']


    projection1 = {'Verification-code': 1, '_id': 0}

    codes = [code['Verification-code'] for code in Liqour_collection.find({}, projection1)]

    projection = {'Brand': 1, 'Category': 1, 'Package': 1, 'ABV': 1, '_id': 0}
    Liqour = list(Liqour_collection.find({}, projection))

    liqour_info = Liqour_collection.find_one({'Verification-code': incoming_message})

    global the_response  # Make sure to use the global variable

    if incoming_message in codes:
        the_response = f"Verified!!The alcohol you bought is a genuine product from EABL "
        the_response += f"Brand: {liqour_info['Brand']} "
        the_response += f"Packaging: {liqour_info['Package']} "
        the_response += f"ABV: {liqour_info['ABV']} "
        the_response += f"Category: {liqour_info.get('Category', 'N/A')} "

        Liqour_collection.delete_one({'Verification-code' : incoming_message})
        
        the_response += f" This specific bottle is hereby no longer available for sell"
    else:
        the_response = "Warning!! Invalid code. Please check the verification code you entered. Please ensure you verify your drink before you consume. Tafadhali hakikisha umedhibitisha uhalisia wa kinywaji chako kabla ya kunywa."
    
    #Send the response message sms via Twilio:
    send_sms(the_response, specifi_phone_number)

    return jsonify({'response_message': the_response})

#send-sms function:
def send_sms(message,to):
    from twilio.rest import Client
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body = message,
        from_ = twilio_phone_number,
        to = to)


