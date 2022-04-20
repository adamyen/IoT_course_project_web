import json
from flask import Flask, render_template
from flask_socketio import SocketIO, send
import wiotp.sdk.application

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

TOPICS = ["CustomerId"]

def mqtt_sub_callback(evt):
    payload = json.dumps(evt.data).strip("{\" }").replace('"','').split(":")
    print(f">>> payload: {payload}")
    if payload[0] == TOPICS[0]:
        user_id = payload[1].lstrip(' ')
        user_scanned_item_topic = f"{user_id}:scanned_item"
        suggestion_topic = f"{user_id}:suggestion"
        for topic in [user_scanned_item_topic, suggestion_topic]:
            print(topic)
            client.subscribeToDeviceEvents(eventId=topic)
    else:
        prefix = 'item' if payload[1] == 'scanned_item' else 'sug'
        print(f"{prefix}-{payload[2].lstrip(' ')}")
        send('foo', f"{prefix}-{payload[2].lstrip(' ')}")

def publish(client, topic, payload, qos = 2, retain = False):
    result = client.publish(topic, payload, qos, retain)
    status = result[0]
    if status == 0:
        print(f"Send to topic `{topic}`:    {payload}")
    else:
        print(f"Failed to send message to topic {topic}")

@socketio.on('connected')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

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
    socketio.run(app)