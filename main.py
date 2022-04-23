import os
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
import wiotp.sdk.application
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv('HOST')
print(f">>> Hosting: {HOST}:5000")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
TOPICS = ["CustomerId"]
# Opening JSON file
f = open('products.json')
product_price = json.load(f)
sum = 0
user_id = 0

def mqtt_sub_callback(evt):
    global user_id
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    print(f">>> payload: {payload}")
    if payload[0] == TOPICS[0]:
        user_id = payload[1].lstrip(' ')
        user_scanned_item_topic = f"{user_id}:scanned_item"
        suggestion_topic = f"{user_id}:suggestion"
        for topic in [user_scanned_item_topic, suggestion_topic]:
            print(topic)
            client.subscribeToDeviceEvents(eventId=topic)
        socketio.send(f"con-{user_id}")
    else:
        prefix = 'item' if payload[1] == 'scanned_item' else 'sug'
        item = payload[2].lstrip(' ')
        print(f"{prefix}-{item}")
        socketio.send(f"{prefix}-{item}")
        if prefix == 'item':
            send_total(item)

def send_total(product):
    global sum
    print(f'>>> Price: {product_price[product]}')
    sum += product_price[product]
    sum = round(sum, 2)
    socketio.send(f"sum-{sum}")  

@socketio.on('connected')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@socketio.on('checkout')
def handle_checkout():
    global sum
    result = client.publishEvent(typeId="RaspberryPi", deviceId="project", eventId=f"{user_id}:reset", msgFormat="json", data={'action': 'reset'}, qos = 2)
    sum = 0
    print(f"-----> Check out complete: {result}")

@app.route("/")
def hello_world():
    return render_template('index.html')

print('1')
options = wiotp.sdk.application.parseConfigFile("application.yaml")
print('2')
client = wiotp.sdk.application.ApplicationClient(config=options)
print('3')
client.connect()
print('4')
for t in TOPICS:
    client.subscribeToDeviceEvents(eventId=t)
print('5')
client.deviceEventCallback = mqtt_sub_callback
print('6')

if __name__ == '__main__':
    socketio.run(app, host=HOST)
