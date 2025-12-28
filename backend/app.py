from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODEL ----------------
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend running"}), 200


@app.route("/expenses", methods=["GET"])
def get_expenses():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify([
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "note": e.note,
            "date": e.date.strftime("%Y-%m-%d")
        }
        for e in expenses
    ]), 200


@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid data"}), 400

    expense = Expense(
        amount=float(data["amount"]),
        category=data["category"],
        note=data.get("note", "")
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({"message": "Expense added"}), 201


@app.route("/analytics/total", methods=["GET"])
def analytics_total():
    total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    return jsonify({"total": total})


@app.route("/analytics/categories", methods=["GET"])
def analytics_categories():
    results = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).group_by(Expense.category).all()

    return jsonify([
        {"category": r[0], "total": r[1]}
        for r in results
    ])


if __name__ == "__main__":
    app.run(debug=True)
