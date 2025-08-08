from flask import Flask, render_template, request, jsonify
from clickhouse_driver import Client
import datetime
import uuid

app = Flask(__name__)

# Function to create a new client each time
def get_client():
    return Client(
        host='clickhouse',
        user='admin',
        password='admin',
        database='mydb'
    )

# Initialize table (safe to do once at startup)
client = get_client()
client.execute('''
CREATE TABLE IF NOT EXISTS todos (
    id String,
    task String,
    created_at DateTime
) ENGINE = ReplacingMergeTree()
ORDER BY (id)
''')
client.disconnect()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    client = get_client()
    rows = client.execute("SELECT id, task, created_at FROM todos ORDER BY created_at DESC")
    client.disconnect()
    tasks = [{"id": r[0], "task": r[1], "created_at": r[2].strftime("%Y-%m-%d %H:%M:%S")} for r in rows]
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    task = data.get("task", "").strip()
    if task:
        task_id = str(uuid.uuid4())
        now = datetime.datetime.now()
        client = get_client()
        client.execute("INSERT INTO todos (id, task, created_at) VALUES", [(task_id, task, now)])
        client.disconnect()
        return jsonify({"status": "success", "id": task_id})
    return jsonify({"status": "error", "message": "Task cannot be empty"}), 400

@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    client = get_client()
    client.execute(f"ALTER TABLE todos DELETE WHERE id='{task_id}'")
    client.disconnect()
    return jsonify({"status": "success"})

@app.route("/chart-data", methods=["GET"])
def chart_data():
    client = get_client()
    rows = client.execute("""
        SELECT toDate(created_at) AS date, count(*) AS total
        FROM todos
        GROUP BY date
        ORDER BY date
    """)
    client.disconnect()
    data = [{"date": str(r[0]), "total": r[1]} for r in rows]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
