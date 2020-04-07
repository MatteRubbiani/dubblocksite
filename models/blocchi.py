from db import db

class BloccoModel(db.Model):
    __tablename__ = "blocchi"

    id = db.Column(db.Integer, primary_key=True)
    lobby_id = db.Column(db.Integer)
    corsia = db.Column(db.Integer)
    livello = db.Column(db.Integer)

    def __init__(self, lobby_id, corsia, livello):
        self.id = None
        self.lobby_id = lobby_id
        self.corsia = corsia
        self.livello = livello

    @classmethod
    def find_by_id(cls, id):
        return BloccoModel.query.filter_by(id=id).first()

    @classmethod
    def find_all_by_lobby_id(cls, lobby_id):
        list = BloccoModel.query.filter_by(lobby_id=lobby_id)
        list1 = []
        for i in list:
            list1.append(i)
        return list1


    @classmethod
    def delete_all_by_lobby_id(cls, lobby_id):
        a = cls.find_all_by_lobby_id(lobby_id)
        for i in a:
            i.delete_from_db()

    @classmethod
    def delete_all(cls):
        for i in BloccoModel.query:
            i.delete_from_db()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
