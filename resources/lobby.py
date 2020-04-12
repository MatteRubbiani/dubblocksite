from flask_restful import Resource, request

from models.users import UserModel
from models.lobbies import LobbyModel
from models.blocchi import BloccoModel
from models.turns import TurnModel


class CreateLobby(Resource):
    def post(self):
        lobby = LobbyModel()
        lobby.save_to_db()
        user = UserModel(lobby_id=lobby.id)
        user.save_to_db()
        LobbyModel.erase_unused()
        return [lobby.tag, user.id]


class CreateUser(Resource):
    def post(self, lobby_tag):
        lobby = LobbyModel.find_by_tag(lobby_tag)
        if not lobby:
            return "bleah", 432
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
        winners_array = []
        users = UserModel.find_all_by_lobby_id_and_status(lobby.id, game_status + 1)
        users.sort(key=lambda x: x.id)
        for u in users:
            c = None
            u_id = u.id
            if u.id == user.id:
                c = u.corsia
            is_playing = False
            if lobby.status == 1 and lobby.find_player_playing().id == u.id:
                is_playing = True
            if u.livello >= lobby.livelli:
                winners_array.append({"id": u.id,
                                      "pedina_number": u.pedina_number})
            else:
                j_user = {"id": u_id, "livello": u.livello, "pedina_number": u.pedina_number, "corsia": c,
                          "is_playing": is_playing, "jolly_reveal": u.jolly_reveal,
                          "jolly_earthquake": u.jolly_earthquake}
                users_array.append(j_user)
        j_griglia = {"corsie": lobby.corsie, "livelli": lobby.livelli, "status": game_status}
        j_result = {
            "griglia": j_griglia,
            "blocchi": blocchi_array,
            "users": users_array,
            "winners": winners_array
        }
        return j_result


class GetLobbyStatus(Resource):
    def get(self, lobby_tag):
        lobby = LobbyModel.find_by_tag(lobby_tag)
        if not lobby:
            return 2, 200
        return lobby.status, 200


class GetUsersInPrepartita(Resource):
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        if not lobby:
            return "ah, ah", 402
        if lobby.status == 1:
            return "match has started", 401
        users = UserModel.find_all_by_lobby_id_and_status(lobby.id, 1)
        j_users = []
        for u in users:
            j_users.append({
                "id": u.id,
                "pedina_number": u.pedina_number
            })
        for i in j_users:
            if i["id"] == user_id:
                j_users.remove(i)
                j_users.append(i)
                break
        return j_users


class DeleteUser(Resource):
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return "no such user", 400
        user.delete_from_db()
        return "user deleted successfully", 200


# ================== partite =================== #

class ResetPartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        users = UserModel.find_all_by_lobby_id(lobby.id)
        for u in users:
            u.status = 0
            u.save_to_db()
        lobby.status = 0
        lobby.save_to_db()

        return "ok", 200


class GetInPrepartita(Resource):
    def post(self, user_id):
        data = request.get_json()
        pedina_number = int(data["pedina_number"])
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        user_ = UserModel.find_by_lobby_id_and_pedina_number(lobby_id=lobby.id, pedina_number=pedina_number)
        if user_:
            return "pedina already taken", 401
        if lobby.status == 0:
            user.status = 1
            user.pedina_number = pedina_number
            user.save_to_db()
            return "user in", 200
        return "match has already started", 400


class LeavePartita(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        user.status = 0
        user.pedina_number = -1
        user.save_to_db()
        lobby = LobbyModel.find_by_id(user.lobby_id)
        lobby.update_turn()
        return "user out", 200


class StartPartita(Resource):
    def post(self, user_id):
        data = request.get_json()
        blocchi = int(data["blocchi"])
        corsie = int(data["corsie"])
        livelli = int(data["livelli"])
        if blocchi > corsie:
            return "troppi blocchi", 406
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        if lobby.status == 1:
            return "match has already started", 403
        # RANDOM POSITION
        user.give_random_corsia(lobby.corsie)
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
            u.pedina_number = 0
            u.save_to_db()

        lobby.update_turn()
        lobby.blocchi = blocchi
        lobby.livelli = livelli
        lobby.corsie = corsie
        lobby.save_to_db()
        lobby.create_blocks()
        return "match started", 200

    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        lobby = LobbyModel.find_by_id(user.lobby_id)
        if not lobby:
            return "ah ah", 401
        j_result = {
            "blocchi": lobby.blocchi,
            "corsie": lobby.corsie,
            "livelli": lobby.livelli
        }
        return j_result


class Passa(Resource):
    def post(self, user_id):
        user = UserModel.find_by_id(user_id)
        turn = TurnModel.find_by_lobby_id(int(user.lobby_id))
        if turn.find_current() != user.id:
            return "mmmmh", 400
        turn.update()
        return "updated", 200


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
                turn.update()
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
        lobby = LobbyModel.find_by_id(user.lobby_id)
        if lobby.find_player_playing().id == user.id:
            user.corsia = int(corsia)
            user.livello = int(livello)
            user.save_to_db()
            turn = TurnModel.find_by_lobby_id(lobby.id)
            turn.update()
            return "ok", 200
        else:
            return "not you turn", 400


# ================== jolly ==================== #

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
