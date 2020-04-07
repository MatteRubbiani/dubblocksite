from db import db

class MatchModel(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.Integer)
    status = db.Column(db.Integer)
    players = db.Column(db.String(100))

    def __init__(self, lobby_id, current=0, array=""):
        self.id = None
        self.lobby_id = lobby_id
        self.current = current
        self.array = array

    @classmethod
    def find_by_id(cls, id):
        return MatchModel.query.filter_by(id=id).first()

    @classmethod
    def find_all_by_lobby_id(cls, lobby_id):
        list = MatchModel.query.filter_by(lobby_id=lobby_id)
        list1 = []
        for i in list:
            list1.append(i)
        return list1

    @classmethod
    def delete_all(cls):
        for i in MatchModel.query:
            i.delete_from_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
