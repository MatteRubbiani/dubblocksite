from db import db
import random
import time
random.seed = time.time()

class TurnModel(db.Model):
    __tablename__ = "turns"

    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.Integer)
    current = db.Column(db.Integer)
    array = db.Column(db.String(100))

    def __init__(self, lobby_id, current=0, array=""):
        self.id = None
        self.lobby_id = lobby_id
        self.current = current
        self.array = array

    @classmethod
    def find_by_id(cls, id):
        return TurnModel.query.filter_by(id=id).first()

    @classmethod
    def find_by_lobby_id(cls, lobby_id):
        return TurnModel.query.filter_by(lobby_id=lobby_id).first()


    @classmethod
    def delete_all(cls):
        for i in TurnModel.query:
            i.delete_from_db()


    def update(self):
        a = self.array.split(",")
        if self.current >= len(a) - 1:
            random.shuffle(a)
            self.array = "".join(a)
            self.current = 0
        else:
            self.current += 1
        self.save_to_db()


    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
