from flask import Flask

class Shop():
	id = None
	logo = None
	title = None
	description = None

	def __init__(self, id, logo = "jhdun.jpg", title = "title", description = "empty"):
		id = id
		self.logo = logo
		self.title = title
		self.description = description