from db import db

from libs.functions import generate_tag

import random

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(20), primary_key=True)
    lobby_id = db.Column(db.Integer)
    corsia = db.Column(db.Integer)
    livello = db.Column(db.Integer)
    pedina_number = db.Column(db.Integer)
    status = db.Column(db.Integer)  # 0 se non in partita, 1 se in prepartita, 2 se in partita
    jolly_reveal = db.Column(db.Integer)
    jolly_earthquake = db.Column(db.Integer)

    def __init__(self, lobby_id=None):
        tag = generate_tag()
        while UserModel.find_by_id(tag):
            tag = generate_tag()
        self.id = tag
        self.lobby_id = lobby_id
        self.corsia = 0
        self.livello = 0
        self.pedina_number = -1
        self.status = 0
        self.jolly_earthquake = 0
        self.jolly_reveal = 0

    def give_random_corsia(self, corsie):
        self.corsia = random.randint(0, int(corsie))
        self.save_to_db()

    @classmethod
    def find_by_id(cls, id):
        return UserModel.query.filter_by(id=id).first()

    @classmethod
    def find_all_by_lobby_id(cls, lobby_id):
        list = UserModel.query.filter_by(lobby_id=lobby_id)
        list1 = []
        for i in list:
            list1.append(i)
        return list1

    @classmethod
    def find_all_by_lobby_id_and_status(cls, lobby_id, status):
        list = UserModel.query.filter_by(lobby_id=lobby_id, status=status)
        list1 = []
        for i in list:
            list1.append(i)
        return list1

    @classmethod
    def find_by_lobby_id_and_pedina_number(cls, lobby_id, pedina_number):
        return UserModel.query.filter_by(lobby_id=lobby_id, pedina_number=pedina_number).first()


    @classmethod
    def delete_all(cls):
        for i in UserModel.query:
            i.delete_from_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
