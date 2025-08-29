from ..database.dbConnection import db

class ModelDataset(db.Model):
    __tablename__ = 'model_datasets'
    modelId = db.Column(db.Integer, db.ForeignKey('models.id'), primary_key=True, nullable=False)
    datasetId = db.Column(db.Integer, db.ForeignKey('datasets.id'), primary_key=True, nullable=False)
    usageType = db.Column(db.String(20), nullable=False)
    createdOn = db.Column(db.DateTime(), nullable=False)
