from flask import Flask, jsonify, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

SECRET_API = '7777777777777'

db = SQLAlchemy()

app = Flask(__name__)


# Group responses in one json
def big_json(scalars):
    list_scalars = []
    for scalar in scalars:
        scalar_json = {
            "id": scalar.id,
            "name": scalar.name,
            "map_url": scalar.map_url,
            "img_url": scalar.img_url,
            "location": scalar.location,
            "seats": scalar.seats,
            "has_toilet": scalar.has_toilet,
            "has_wifi": scalar.has_wifi,
            "has_sockets": scalar.has_sockets,
            "can_take_calls": scalar.can_take_calls,
            "coffee_price": scalar.coffee_price
        }
        list_scalars.append(scalar_json)
    return list_scalars


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///7777.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random_cafe():
    cafe = db.session.execute(db.select(Cafe).order_by(func.random())).scalar()
    return jsonify(
        id=cafe.id,
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        seats=cafe.seats,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        has_sockets=cafe.has_sockets,
        can_take_calls=cafe.can_take_calls,
        coffee_price=cafe.coffee_price
    )


@app.route('/all')
def all_cafes():
    cafes = db.session.execute(db.select(Cafe)).scalars()
    list_cafes = big_json(cafes)
    return jsonify(cafes=list_cafes)


@app.route('/search')
def search():
    loc = request.args.get('loc')
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars()
    list_cafes = big_json(cafes)
    if len(list_cafes) > 0:
        return jsonify(cafes=list_cafes)
    else:
        not_found = {'Not found': "Sorry, we don't have a cafe at that location."}
        return jsonify(error=not_found)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        cafe = Cafe(
            name=request.form['name'],
            map_url=request.form['map_url'],
            img_url=request.form['img_url'],
            location=request.form['location'],
            seats=request.form['seats'],
            has_toilet=bool(request.form['has_toilet']),
            has_wifi=bool(request.form['has_wifi']),
            has_sockets=bool(request.form['has_sockets']),
            can_take_calls=bool(request.form['can_take_calls']),
            coffee_price=bool(request.form['coffee_price'])
        )
        db.session.add(cafe)
        db.session.commit()
        response = {"success": "Successfully added  the new cafe."}
        return jsonify(response=response)


@app.route('/update-price/<int:cafe_id>', methods=['GET', 'PATCH'])
def update_price(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)

    new_price = request.args.get('new_price')
    if request.method == 'PATCH':
        cafe.coffee_price = f'€{new_price}'
        db.session.add(cafe)
        db.session.commit()
        return jsonify(success="Successfully updated the price.")


@app.route('/delete/<int:cafe_id>', methods=['GET', 'DELETE'])
def delete_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    api = request.args.get('api_key')

    if request.method == 'DELETE':
        if api == SECRET_API:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success='Successfully deleted the cafe.')
        else:
            return Response(
                "{'error':'Sorry that's not allowed. Make sure you have the correct api_key'}",
                status=403,
                mimetype='application/json'
            )


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
