import os, threading, time, json, sqlite3
from flask import Flask
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv('PROJECT_ID')
TOPIC_ID   = os.getenv('TOPIC_ID')
PORT       = int(os.getenv('PORT','8080'))

# DB local
conn = sqlite3.connect('generator.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
  CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )''')
conn.commit()

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

app = Flask(__name__)

def generator_loop():
    counter = 0
    while True:
        counter += 1
        task = {'id': counter, 'value': counter * 2}
        c.execute('INSERT INTO tasks (payload) VALUES (?)', (json.dumps(task),))
        conn.commit()
        publisher.publish(topic_path, json.dumps(task).encode('utf-8'))
        print(f"Generated task {task}")
        time.sleep(5)

@app.route('/')
def health():
    return 'OK', 200

if __name__=='__main__':
    t = threading.Thread(target=generator_loop, daemon=True)
    t.start()
+    app.run(host='0.0.0.0', port=PORT, use_reloader=False)

