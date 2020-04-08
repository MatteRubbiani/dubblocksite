from flask_restful import Resource, request

from models.users import UserModel
from models.lobbies import LobbyModel
from models.blocchi import BloccoModel
from models.turns import TurnModel


class CreateLobby(Resource):
    def post(self):
        lobby = LobbyModel()
        lobby.save_to_db()

        lobby.create_blocks()
        user = UserModel(lobby_id=lobby.id)
        user.save_to_db()
        return [lobby.tag, user.id]

class CreateUser(Resource):
    def post(self, lobby_tag):
        lobby = LobbyModel.find_by_tag(lobby_tag)
        user = UserModel(lobby_id=lobby.id)
        user.save_to_db()
        return user.id

class GetGrid(Resource):
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        blocchi_array = []
        blocchi = BloccoModel.find_all_by_lobby_id(lobby.id)
        for b in blocchi:
            j_bloc = {"id": b.id, "corsia": b.corsia, "livello": b.livello}
            blocchi_array.append(j_bloc)
        game_status = lobby.status
        users_array = []
        users = UserModel.find_all_by_lobby_id_and_status(lobby.id, game_status + 1)
        for u in users:
            c = None
            if u.id == user.id:
                c = u.corsia
            is_playing = False
            if lobby.status == 1 and lobby.find_player_playing().id == u.id:
                is_playing = True
            j_user = {"id": u.id, "livello": u.livello, "pedina_number": u.pedina_number, "corsia": c,
                      "is_playing": is_playing, "jolly_reveal": u.jolly_reveal, "jolly_earthquake": u.jolly_earthquake }
            users_array.append(j_user)
        j_griglia = {"corsie": lobby.corsie, "livelli": lobby.livelli, "status": game_status}
        j_result = {
            "griglia": j_griglia,
            "blocchi": blocchi_array,
            "users": users_array
        }
        return j_result

class GetLobbyStatus(Resource):
    def get(self, lobby_tag):
        lobby = LobbyModel.find_by_tag(lobby_tag)
        if not lobby:
            return 2, 400
        return lobby.status, 200

# ================== partite =================== #

class ResetPartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.id)
        users = UserModel.find_all_by_lobby_id(lobby.id)
        for u in users:
            u.status = 0
            u.save_to_db()
        lobby.status = 0
        lobby.save_to_db()

        return "ok", 200


class GetInPrepartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        if lobby.status == 0:
            user.status = 1
            user.save_to_db()
            return "user in", 200
        return "match has already started", 400


class LeavePartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        user.status = 0
        user.save_to_db()
        lobby = LobbyModel.find_by_id(user.lobby_id)
        lobby.update_turn()
        return "user out", 200


class StartPartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        lobby.status = 1
        users = UserModel.find_all_by_lobby_id_and_status(lobby.id, 1)
        for u in users:
            u.status = 2
            u.jolly_earthquake = 1
            u.jolly_reveal = 1
            u.save_to_db()
        n_users = UserModel.find_all_by_lobby_id_and_status(lobby.id, 0)
        for u in n_users:
            u.jolly_earthquake = 0
            u.jolly_reveal = 0
            u.save_to_db()
        lobby.update_turn()
        return "match started", 200

# ================= gameplay =================== #

class MoveBlocco(Resource):
    def post(self, user_id, blocco_id):
        data = request.get_json()
        corsia = data["corsia"]
        livello = data["livello"]
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        blocco = BloccoModel.find_by_id(int(blocco_id))
        if lobby.find_player_playing().id == user.id:
            if blocco.lobby_id == lobby.id:
                blocco.corsia = int(corsia)
                blocco.livello = int(livello)
                blocco.save_to_db()
                turn = TurnModel.find_by_lobby_id(lobby.id)
                turn.update
                turn.save_to_db()
                return "ok", 200
            return "ma cosa", 400
        else:
            return "not you turn", 400

class Move(Resource):
    def post(self, user_id):
        data = request.get_json()
        corsia = data["corsia"]
        livello = data["livello"]
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.id)
        if lobby.find_player_playing().id == user.id:
            user.corsia = int(corsia)
            user.livello = int(livello)
            user.save_to_db()
            turn = TurnModel.find_by_lobby_id(lobby.id)
            turn.update
            return "ok", 200
        else:
            return "not you turn", 400

# JOLLLLLLLYYYY

class JollyReveal(Resource):
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user.jolly_reveal < 1:
            return "ah ah", 400
        user.jolly_reveal = 0
        user.save_to_db()
        lobby = LobbyModel.find_by_id(user.lobby_id)
        blocchi_array = []
        blocchi = BloccoModel.find_all_by_lobby_id(lobby.id)
        for b in blocchi:
            j_bloc = {"id": b.id, "corsia": b.corsia, "livello": b.livello}
            blocchi_array.append(j_bloc)
        game_status = lobby.status
        users_array = []
        users = UserModel.find_all_by_lobby_id_and_status(lobby.id, game_status + 1)
        for u in users:
            c = u.corsia
            is_playing = False
            if lobby.status == 1 and lobby.find_player_playing().id == u.id:
                is_playing = True
            j_user = {"id": u.id, "livello": u.livello, "pedina_number": u.pedina_number, "corsia": c,
                      "is_playing": is_playing}
            users_array.append(j_user)
        j_griglia = {"corsie": lobby.corsie, "livelli": lobby.livelli, "status": game_status}
        j_result = {
            "griglia": j_griglia,
            "blocchi": blocchi_array,
            "users": users_array
        }
        return j_result

class JollyEarthquake(Resource):
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user.jolly_earthquake < 1:
            return "ah ah", 400
        lobby = LobbyModel.find_by_id(user.lobby_id)
        lobby.create_blocks()
        user.jolly_earthquake = 0
        user.save_to_db()
        return "ok", 200
