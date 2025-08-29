from ..database.dbConnection import db

class Dataset(db.Model):
    __tablename__ = 'datasets'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    datasetType = db.Column(db.String(20), nullable=False)
    s3Path = db.Column(db.String(500), nullable=True)
    createdBy = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    createdOn = db.Column(db.DateTime(), nullable=False)

