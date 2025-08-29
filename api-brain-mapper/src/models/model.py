from ..database.dbConnection import db

class Model(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    modelType = db.Column(db.String(100), nullable=False)
    createdOn = db.Column(db.DateTime(), nullable=False)
    updatedOn = db.Column(db.DateTime(), nullable=True)
