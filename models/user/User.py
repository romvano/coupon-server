from flask import Flask

class User():
	id = 1
	login = None
	password = None

	def __init__(self, login, password, id=1):
		self.login = login
		self.password = password
		self.id = id

	def is_authenticated(self):
		return False

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	def __repr__(self):
		return '<User %d: %r' % (self.id, self.login)