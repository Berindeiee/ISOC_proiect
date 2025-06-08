from google.cloud import pubsub_v1
from google.cloud import firestore
import json

PROJECT_ID = 'your-gcp-project'
SUBSCRIPTION_ID = 'tasks-sub'

# Initialize Firestore
db = firestore.Client()

# Initialize Pub/Sub subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def callback(message):
    task = json.loads(message.data.decode('utf-8'))
    result = {'task_id': task['id'], 'processed_value': task['value'] + 100}
    # store result in Firestore
    db.collection('results').add(result)
    print(f"Processed and stored result: {result}")
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for tasks on {subscription_path}')

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
