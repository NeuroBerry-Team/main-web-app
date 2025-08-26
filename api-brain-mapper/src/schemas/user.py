from ..models.user import User
from .inference import inference_schema
from .role import role_schema
from ..database.serializers_utils import ma

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ["password"]
    
    # Nested schema for role
    role = ma.Nested(role_schema)

    # Setup a nested schema to serialize inferences
    inferences = ma.Nested(inference_schema, many=True)

user_schema = UserSchema()