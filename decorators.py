def valid_command(command):
	def new_function(self, *args, **kwargs):
		if all(key in kwargs for key in ('sender', 'channel')):
			command(self, *args, **kwargs)
		else:
			raise Exception('missing sender and or channel')
	new_function.__name__ = command.__name__
	new_function.valid_command = True
	return new_function
