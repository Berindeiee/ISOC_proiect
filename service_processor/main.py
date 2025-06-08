import os, threading, json
from flask import Flask
from google.cloud import pubsub_v1, firestore

# Config din env
PROJECT_ID     = os.getenv('PROJECT_ID')
SUBSCRIPTION_ID= os.getenv('SUBSCRIPTION_ID')
PORT           = int(os.getenv('PORT', '8080'))

# Setup Firestore
db = firestore.Client()

# Setup Pub/Sub subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

app = Flask(__name__)

def callback(message):
    task = json.loads(message.data.decode('utf-8'))
    result = {'task_id': task['id'], 'processed_value': task['value'] + 100}
    db.collection('results').add(result)
    print(f"Processed and stored result: {result}")
    message.ack()

def processor_loop():
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull.result()
    except Exception:
        streaming_pull.cancel()

@app.route('/')   # health-check
def health():
    return 'OK', 200

if __name__ == '__main__':
    t = threading.Thread(target=processor_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=PORT, use_reloader=False)
