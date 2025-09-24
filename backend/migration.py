from database import Base, engine
from repositories.models.models import User, Messages, Conversation, MessageRole

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Finish creating tables...")