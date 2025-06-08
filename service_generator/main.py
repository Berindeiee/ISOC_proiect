import os, threading, time, json, sqlite3, random, datetime
from faker import Faker
from flask import Flask
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_ID   = os.getenv('TOPIC_ID')
PORT       = int(os.getenv('PORT','8080'))

# DB local
conn = sqlite3.connect('generator.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
  CREATE TABLE IF NOT EXISTS orders (
    order_id      INTEGER PRIMARY KEY,
    customer_name TEXT,
    product       TEXT,
    quantity      INTEGER,
    price         REAL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
''')
conn.commit()

# Setup Faker şi Pub/Sub
fake = Faker()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

app = Flask(__name__)

def generator_loop():
    order_id = 0
    while True:
        order_id += 1
        # generează date realiste
        order = {
            'order_id': order_id,
            'customer_name': fake.name(),
            'product': fake.word().title(),
            'quantity': random.randint(1, 5),
            'price': round(random.uniform(10.0, 200.0), 2),
            'ordered_at': datetime.datetime.utcnow().isoformat() + 'Z'
        }
        # stochează local
        c.execute('''
          INSERT INTO orders (order_id, customer_name, product, quantity, price)
          VALUES (?, ?, ?, ?, ?)
        ''', (order['order_id'], order['customer_name'], order['product'],
              order['quantity'], order['price']))
        conn.commit()
        # publică în Pub/Sub
        publisher.publish(topic_path, json.dumps(order).encode('utf-8'))
        print(f"Generated order {order}", flush=True)
        time.sleep(10)

@app.route('/')
def health():
    return 'OK', 200

if __name__=='__main__':
    t = threading.Thread(target=generator_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=PORT, use_reloader=False)
