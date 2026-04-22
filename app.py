from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import traceback
import os

app = Flask(__name__)
CORS(app)
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["taskflow"]
tasks_col = db["tasks"]
diary_col = db["diary"]


def to_dict(doc):
    """Turn a MongoDB doc into a plain dict (convert ObjectId → str)."""
    doc["_id"] = str(doc["_id"])
    return doc
@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        tasks = list(tasks_col.find().sort("createdAt", -1))
        return jsonify([to_dict(t) for t in tasks]), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/tasks", methods=["POST"])
def add_task():
    try:
        data = request.get_json()
        if not data or not data.get("title", "").strip():
            return jsonify({"error": "title is required"}), 400

        task = {
            "title":     data["title"].strip(),
            "priority":  data.get("priority", "medium"),
            "deadline":  data.get("deadline", ""),
            "completed": data.get("completed", False),
            "subtasks":  data.get("subtasks", []),
            "createdAt": data.get("createdAt", datetime.utcnow().isoformat()),
        }
        result   = tasks_col.insert_one(task)
        task["_id"] = str(result.inserted_id)
        return jsonify(task), 201
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json()
        data.pop("_id", None)
        tasks_col.update_one({"_id": ObjectId(task_id)}, {"$set": data})
        updated = tasks_col.find_one({"_id": ObjectId(task_id)})
        return jsonify(to_dict(updated)), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        tasks_col.delete_one({"_id": ObjectId(task_id)})
        return jsonify({"message": "Task deleted"}), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/diary", methods=["GET"])
def get_diary():
    try:
        entries = list(diary_col.find().sort("date", -1))
        return jsonify([to_dict(e) for e in entries]), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/diary", methods=["POST"])
def add_diary():
    try:
        data = request.get_json()
        if not data or not data.get("content", "").strip():
            return jsonify({"error": "content is required"}), 400

        entry = {
            "content": data["content"].strip(),
            "date":    data.get("date", datetime.utcnow().isoformat()),
        }
        result = diary_col.insert_one(entry)
        entry["_id"] = str(result.inserted_id)
        return jsonify(entry), 201
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/diary/<entry_id>", methods=["PUT"])
def update_diary(entry_id):
    try:
        data = request.get_json()
        data.pop("_id", None)
        diary_col.update_one({"_id": ObjectId(entry_id)}, {"$set": data})
        updated = diary_col.find_one({"_id": ObjectId(entry_id)})
        return jsonify(to_dict(updated)), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


@app.route("/diary/<entry_id>", methods=["DELETE"])
def delete_diary(entry_id):
    try:
        diary_col.delete_one({"_id": ObjectId(entry_id)})
        return jsonify({"message": "Diary entry deleted"}), 200
    except Exception:
        return jsonify({"error": traceback.format_exc()}), 500


if __name__ == "__main__":
    print("\n✅  TaskFlow backend running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
