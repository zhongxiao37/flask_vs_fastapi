from flask import Flask
import time
import threading

app = Flask(__name__)

@app.route("/ping")
def ping():
    return {"message": "pong"}

@app.route("/sleep")
def sleep_endpoint():
    time.sleep(5)  # Simulate IO blocking operation
    return {"id": threading.current_thread().native_id, "message": "Woke up after 5 seconds"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000) 