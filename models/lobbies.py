from db import db
from libs.functions import generate_tag

import random
import time

random.seed = time.time()

from .blocchi import BloccoModel
from .turns import TurnModel
from .users import UserModel

class LobbyModel(db.Model):
    __tablename__ = "lobbies"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(40))
    corsie = db.Column(db.Integer)
    livelli = db.Column(db.Integer)
    blocchi = db.Column(db.Integer)
    status = db.Column(db.Integer)  # 0 se non in partita, 1 se in partita

    def __init__(self, corsie=5, livelli=10, blocchi=3):
        self.id = None
        self.corsie = corsie
        self.livelli = livelli
        self.blocchi = blocchi
        self.modify_tag()
        self.create_blocks()
        self.status = 0

    def modify_tag(self):
        tag = generate_tag()
        while self.find_by_tag(tag):
            tag = generate_tag()
        self.tag = tag

    @classmethod
    def find_by_id(cls, id):
        return LobbyModel.query.filter_by(id=id).first()

    @classmethod
    def find_by_tag(cls, tag):
        return LobbyModel.query.filter_by(tag=tag).first()

    @classmethod
    def delete_all(cls):
        for i in LobbyModel.query:
            i.delete_from_db()

    def create_blocks(self):
        BloccoModel.delete_all_by_lobby_id(self.id)
        for liv in range(self.livelli):
            blocchi_in_livello = []
            for i in range(self.blocchi):
                random_corsia = random.randrange(0, self.corsie, 1)
                while random_corsia in blocchi_in_livello:
                    random_corsia = random.randrange(0, self.corsie, 1)
                blocchi_in_livello.append(random_corsia)
            for blocco_corsia in blocchi_in_livello:
                blocco = BloccoModel(self.id, blocco_corsia, liv)
                blocco.save_to_db()

    def update_turn(self):
        turn = TurnModel.find_by_lobby_id(self.id)
        if turn:
            turn.delete_from_db()
        players = UserModel.find_all_by_lobby_id_and_status(self.id, 2)
        random.shuffle(players)
        s_players = ",".join(str(player.id) for player in players)
        turn = TurnModel(self.id, array=s_players)
        turn.save_to_db()

    def find_player_playing(self):
        turn = TurnModel.find_by_lobby_id(self.id)
        a_players = turn.array.split(",")
        current = a_players[turn.current]
        user = UserModel.find_by_id(current)
        return user

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
