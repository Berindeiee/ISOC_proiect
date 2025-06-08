import os, threading, json
from flask import Flask
from google.cloud import pubsub_v1, firestore

# Citire variabile de mediu
PROJECT_ID      = os.getenv('PROJECT_ID')
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID')
PORT            = int(os.getenv('PORT','8080'))

# Conectare la Firestore
db = firestore.Client()

# Subscrber Pub/Sub
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

app = Flask(__name__)

def callback(message):
    raw = message.data.decode('utf-8')
    try:
        order = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[WARN] Mesaj invalid JSON, îl ignor: {raw}", flush=True)
        message.ack()
        return

    # Exemplu de procesare: calculează totalul comenzii
    total_amount = order['quantity'] * order['price']

    # Construieşte documentul
    doc = {
        'order_id':      order['order_id'],
        'customer_name': order['customer_name'],
        'product':       order['product'],
        'quantity':      order['quantity'],
        'price':         order['price'],
        'ordered_at':    order['ordered_at'],
        'total_amount':  total_amount,
        'processed_at':  firestore.SERVER_TIMESTAMP
    }

    # Scrie în Firestore în colecția `orders`
    db.collection('orders').add(doc)
    print(f"Processed order {order['order_id']}, total={total_amount}", flush=True)
    message.ack()

def processor_loop():
    print(f">> Pornesc processor-ul, subscribe la {subscription_path}", flush=True)
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull.result()
    except Exception as e:
        print("Eroare în processor_loop:", e, flush=True)
        streaming_pull.cancel()

@app.route('/')   # health-check
def health():
    return 'OK', 200

if __name__ == '__main__':
    t = threading.Thread(target=processor_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=PORT, use_reloader=False)
