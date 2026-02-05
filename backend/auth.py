from collections import namedtuple
import uuid

User = namedtuple("User", ["id", "email"])

def get_current_user():
    # TODO: Implement actual JWT authentication
    # This is a mock user for development purposes
    return User(id=uuid.uuid4(), email="test@example.com")
