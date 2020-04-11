import os
from flask import Flask
from flask_restful import Api

from flask_cors import CORS
from flask import render_template

from resources.lobby import CreateLobby, CreateUser, GetGrid, ResetPartita, GetInPrepartita, \
    LeavePartita, StartPartita, MoveBlocco, Move, JollyEarthquake, JollyReveal, GetLobbyStatus, GetUsersInPrepartita, DeleteUser, Passa

# ============ app configs ============= #

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['CORS_HEADERS'] = '*'
api = Api(app)
cors = CORS(app)

# ============ not found ============= #

"""@app.errorhandler(404)
def page_not_found(e):
    return render_template("not_found.html",
                           message="Oops. Looks something's wrong. Check the spelling and try again"), 404
"""
# ============ app routes ============= #


# ============  server endpoints ============= #
api.add_resource(CreateLobby, "/create_lobby")
api.add_resource(CreateUser, "/create_user/<string:lobby_tag>")
api.add_resource(GetGrid, "/get/<string:user_id>")
api.add_resource(ResetPartita, "/reset/<string:user_id>")
api.add_resource(GetInPrepartita, "/join_prepartita/<string:user_id>")
api.add_resource(LeavePartita, "/leave_partita/<string:user_id>")
api.add_resource(StartPartita, "/start_partita/<string:user_id>")
api.add_resource(MoveBlocco, "/move_blocco/<string:user_id>/<string:blocco_id>")
api.add_resource(Move, "/move_pedina/<string:user_id>")
api.add_resource(JollyReveal, "/jolly_reveal/<string:user_id>")
api.add_resource(JollyEarthquake, "/jolly_earthquake/<string:user_id>")
api.add_resource(GetLobbyStatus, "/get_lobby_status/<string:lobby_tag>")
api.add_resource(GetUsersInPrepartita, "/get_ready_players/<string:user_id>")
api.add_resource(DeleteUser, "/delete_user/<string:user_id>")
api.add_resource(Passa, "/passa/<string:user_id>")
# ============================================ #

if __name__ == "__main__":
    from db import db


    @app.before_first_request
    def create_table():
        db.create_all()


    db.init_app(app)
    app.run(port=60000, debug=True)
