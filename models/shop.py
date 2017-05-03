from flask import Flask

class Shop():
	iD = None
	logo = None
	title = None
	description = None

	def __init__(self, iD, logo = "jhdun.jpg", title = "title", description = "empty"):
		iD = id
		self.logo = logo
		self.title = title
		self.description = description