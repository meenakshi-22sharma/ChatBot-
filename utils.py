from pymongo import MongoClient
client = MongoClient("mongodb+srv://test:test@cluster0-gdyux.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database('weather_db')
records = db.weather_info
record_pic=db.pic_info


import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"   # json file downloaded  from dialog flow under project-id link

url="https://dog.ceo/api/breeds/image/random"
import requests
import json

#import giphypop
#g = giphypop.Giphy()
#results = [x for x in g.search('cake')]

from giphypop import translate


import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "newsbot-qlpqub"    # https://console.dialogflow.com/api-client/#/editAgent/9db1e3db-93e1-4a18-acf4-20cb206238cc/

from gnewsclient import gnewsclient
client = gnewsclient.NewsClient(max_results = 3)


import pyowm
owm = pyowm.OWM('6f6d5f66162ddf2c5f83c5a0eb975eeb')


def get_weather(parameters):
    print("*************************************************")
    print("PARAMETRES :   ", parameters)
    print("*************************************************")
    print("*************************************************")
    # alwys check paramter name from DialogFLow
    #city="Cambridge"
    #country = "uk"
    city=parameters.get('geo-city')
    #country=parameters.get('geo-country')
    observation = owm.weather_at_place(city)
    w = observation.get_weather()
    wind = w.get_wind()
    temperature = w.get_temperature('celsius')
    tomorrow = pyowm.timeutils.tomorrow()
    
    lis=[wind,temperature]
    #return observation.get_weather()
    return lis

def get_news(parameters):
    print("*************************************************")
    print("PARAMETRES :   ", parameters)
    print("*************************************************")
    print("*************************************************")

    #print(parameters.get('news_type')[0])
    # alwys check paramter name from DialogFLow
    client.topic = parameters.get('new_type') # [0]    if typeerror
    
    client.language = parameters.get('language')
    client.location = parameters.get('geo-country')
    return client.get_news()


def get_jobs(parameters):
    print("*************************************************")
    print("PARAMETRES :   ", parameters)
    print("*************************************************")
    print("*************************************************")
   
    topic = parameters.get('job_type')
    

    city = parameters.get('geo-city')
    if(city==""):
        city="london"
    if(topic==""):
        topic="developer"
    #json_ob = "https://jobs.github.com/positions.json?description={}&location={}".format(topic,country)
    json_ob = "https://jobs.github.com/positions.json?description={}&location={}".format(topic,city)
    reply=requests.get(json_ob)
    return reply.json()

def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

def fetch_reply(msg,session_id):
    response = detect_intent_from_text(msg,session_id)
    if response.intent.display_name == 'get_jobs':
        news = get_jobs( dict(response.parameters))
        
        job_str='Job list : '
        for row in news:
            job_str +="\n\n {} \n\n {} \n\n".format(str(row['type']), str(row['url']))
            
        return ("",job_str)
    elif response.intent.display_name =='image_whatsapp':
        news_str='First, you have to send us an image !'
        return ("image_whatsapp",news_str)


    elif response.intent.display_name == 'get_news':
         news = get_news( dict(response.parameters))

         news_str='Here is your news feed : '
         for row in news:
               news_str +="\n\n {} \n\n {} \n\n".format(row['title'], row['link'])

         return ("",news_str)
    elif response.intent.display_name == 'get_weather':
         weather = get_weather( dict(response.parameters))
         weather_str='Here is your weather info:'
         wind_speed=str(weather[0]['speed'])
         wind_deg=str(weather[0]['deg'])
         temp= str(weather[1]['temp'])
         max_temp=str(weather[1]['temp_max'])
         min_temp=str(weather[1]['temp_min'])
        #for row in weather:
           
        
         result="\n\n  WIND : \n   wind speed:{} km/hr\n   wind deg:{} \n\n  TEMPERATURE : \n   temp:{} °C \n   max-temp:{} °C\n   min-temp:{} °C \n\n".format( wind_speed,wind_deg,temp,max_temp,min_temp)
         weather_str+=result
         new_temp = {
             'wind_speed':wind_speed,
             'wind_deg': wind_deg,
             'temp': temp,
             'temp_min':max_temp,
             'temp_max':min_temp
            }
         records.insert_one(new_temp)
         return ("",weather_str)
    elif response.intent.display_name == 'get_image':

        print("Sending ...image")
        response=requests.get(url)
        link=json.loads(response.text)
        new_pic = {
             'picture_link':link["message"]
             
            }
        record_pic.insert_one(new_pic)
        return("picture",link["message"])
    else:

        return ("",response.fulfillment_text)
     