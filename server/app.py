from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# Routes

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        return [camper.to_dict(rules=('-signups',)) for camper in campers], 200

    def post(self):
        data = request.get_json()

        try:
            new_camper = Camper(
                name=data['name'],
                age=data['age']
            )

            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(rules=('-signups',)), 201

        except Exception:
            return {"errors": ["validation errors"]}, 400


class CamperByID(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return {"error": "Camper not found"}, 404
        return camper.to_dict(), 200

    def patch(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return {"error": "Camper not found"}, 404

        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']

            db.session.commit()
            return camper.to_dict(rules=('-signups',)), 202
        except Exception:
            return {"errors": ["validation errors"]}, 400


class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict(rules=('-signups',)) for activity in activities], 200


class ActivityByID(Resource):
    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return {"error": "Activity not found"}, 404

        db.session.delete(activity)
        db.session.commit()
        return {}, 204


class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                time=data['time'],
                camper_id=data['camper_id'],
                activity_id=data['activity_id']
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 201

        except Exception:
            return {"errors": ["validation errors"]}, 400


# Register routes
api.add_resource(Campers, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
