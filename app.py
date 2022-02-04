import os
from pathlib import Path
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, abort, request

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

db_path = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) if os.environ.get('DATABASE_URL') else None
app.config['SQLALCHEMY_DATABASE_URI'] = db_path or f"sqlite:///{BASE_DIR / 'test.db'}"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "author": {
                "id": self.author.id,
                "name": self.author.name
            }
        }

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


# AUTHORS
@app.route("/authors")
def authors_list():
    authors = AuthorModel.query.all()
    authors = [author.to_dict() for author in authors]
    return jsonify(authors), 200


@app.route("/authors/<int:author_id>")
def author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author in None:
        abort(404)
    return jsonify(author), 200


# @app.route("/authors/<int:author_id>", methods=["PUT"])
# def edit_author(author_id):
#     data = request.json
#     return jsonify(author), 200


@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    author.save()
    return author.to_dict(), 201


# QUOTES
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


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    new_quote = request.json
    q = QuoteModel(author, new_quote["text"])
    db.session.add(q)
    db.session.commit()
    return jsonify(q.to_dict()), 201


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


if __name__ == "__main__":
    app.run(debug=True)
