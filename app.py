from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False)
    text = db.Column(db.String(255), unique=False)
    rate = db.Column(db.Integer, server_default='1')

    def __init__(self, author, text, rate=1):
        self.author = author
        self.text = text
        self.rate = rate

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rate": self.rate
        }

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Quote: {self.author} | {self.text[:10]}..."


@app.route("/quotes/<int:quote_id>")
def quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"Quote with id={quote_id} not found")

    return jsonify(quote.to_dict())


@app.route("/quotes", methods=["GET"])  # <== GET
def quotes_list():
    quotes = QuoteModel.query.all()
    quotes = [q.to_dict() for q in quotes]
    return jsonify(quotes), 200


@app.route("/quotes", methods=["POST"])  # <== POST
def create_quote():
    data = request.json
    new_quote = QuoteModel(**data)
    db.session.add(new_quote)
    db.session.commit()
    return jsonify(new_quote.to_dict()), 201  # 201 - Created


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json

    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"Quote with id={quote_id} not found")

    # if quote := QuoteModel.query.get(quote_id) is None:
    #     abort(404, f"Quote with id={quote_id} not found")

    for key, val in new_data.items():
        setattr(quote, key, val)

    # people = ...
    # people.name = "Вася"
    #
    # attatr = "name"
    # setattr(people, attatr, "Вася")

    db.session.commit()
    return jsonify(quote.to_dict()), 200

@app.route("/quotes/<int:qid>", methods=["DELETE"])
def delete_quote_by_id(qid):
    quote = QuoteModel.query.get(qid)
    if quote is None:
        abort(404, f"Quote with id={qid} not found")

    db.session.delete(quote)
    db.session.commit()
    return jsonify({"message": f"Quote with id {qid} is deleted."}), 200


# @app.route("/quotes/filter", methods=["POST"])  # <== POST
# def filter_quote():
#     data = request.json
#     quotes = QuoteModel.query.filter_by(**data)
#     quotes = [q.to_dict() for q in quotes]
#
#     return jsonify(quotes), 200

if __name__ == "__main__":
    app.run()