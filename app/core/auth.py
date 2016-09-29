from models import users

def login(user):
	print(users.find_one())
	return user == "simon"