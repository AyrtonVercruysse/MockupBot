import websocket, socket, urllib.request, requests, json
import sched, time, traceback
import threading, sys
import datetime
from decorators import *

class MockupBot:
	strings = {}

	def __init__(self, token):
		self.token = token
		self.socket = None
		self.id = 0
		self.sched = sched.scheduler(time.time, time.sleep)
		self.channels = {}
		self.running = True
		self.message_link = 'https://slack.com/api/chat.postMessage'

	def connect(self):
		s = socket.socket()
		resp = urllib.request.urlopen('https://slack.com/api/rtm.start?token=' + self.token).read().decode('utf-8')
		self.socket = websocket.create_connection(json.loads(resp)['url'])
		print(self.socket.recv())

	def ping(self):
		while self.running:
			msg = json.dumps({"id" : self.id, "type" : "ping"})
			self.id = self.id + 1
			self.socket.send(msg)
			time.sleep(15)

	def get_channels(self):
		resp = json.loads(urllib.request.urlopen('https://slack.com/api/channels.list?token=' + self.token).read().decode('utf-8'))
		for c in resp["channels"]:
			self.channels[c["name"]] = c["id"]
		resp = json.loads(urllib.request.urlopen('https://slack.com/api/groups.list?token=' + self.token).read().decode('utf-8'))
		for c in resp["groups"]:
			self.channels[c["name"]] = c["id"]

		print(self.channels)

	def read(self):
		resp = json.loads(self.socket.recv())
		return resp

	def run(self):
		while self.running:
			resp = self.read()
			try:
				if resp["type"] == "pong":
					continue
			except:
				pass

			if not all(key in resp.keys() for key in ('type', 'text')):
				print(resp)
				continue
			if resp['type'] == 'message':
				msg = resp['text']
				if msg[:1] == '!':
					msg 	= msg[1:]
					args 	= msg.split(" ")
					print (msg, args)
					key = args.pop(0)
					try: 
						func = getattr(self, key)
						print(func)
						print(func.valid_command)
						if func.valid_command:
							func(*args, sender=resp['user'], channel=resp['channel'])
					except:
						try:
							value = " ".join(args)
							self.strings[key] = value
							self.send(resp['channel'], 'Ok')
						except:
							self.send(resp['channel'], 'Something went wrong')
							print(resp)
							traceback.print_tb(sys.exc_info()[2])

	@valid_command
	def hoelangnog(self, *args, **kwargs):
		delta = datetime.datetime(2016, 3, 24) - datetime.datetime.now()
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		reply = "Glenn is jarig binnen " + str(days) + " dagen " + str(hours) + " uur " + str(minutes) + " minuten."
		self.send(kwargs['channel'], reply )

	@valid_command
	def enbenoit(self, *args, **kwargs):
		delta =  datetime.datetime(2016, 5, 11) - datetime.datetime.now() 
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		reply = "Benoit is jarig binnen " + str(days) + " dagen " + str(hours) + " uur " + str(minutes) + " minuten."
		self.send(kwargs['channel'], reply )

	@valid_command
	def enayrton(self, *args, **kwargs):
		delta = datetime.datetime.now() - datetime.datetime(2014, 2, 11)
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		reply = "Ayrton verjaart niet meer en is ondertussen al " + str(days) + " dagen " + str(hours) + " uur " + str(minutes) + " minuten 25 jaar"
		self.send(kwargs['channel'], reply )

	@valid_command
	def whois(self, *args, **kwargs):
		strings = self.strings
		reply = args[0]+ " " + strings.get(args[0])
		if not reply:
			# reply = "I do not know " + args[0]
			reply = "I do not know " + args[0]
		self.send(kwargs['channel'], reply )

	@valid_command
	def verjaardag(self, *args, **kwargs):
		if args[0] == "Glenn" or len(args) == 0:
			delta = datetime.datetime(2016, 3, 24) - datetime.datetime.now()
		if args[0] == "Benoit":
			delta = datetime.datetime(2016, 5, 11) - datetime.datetime.now()
		if args[0] == "Ayrton":
			delta = datetime.datetime(2017, 2, 11) - datetime.datetime.now()
		if args[0] == "Matthias":
			delta = datetime.datetime(2016, 4, 9) - datetime.datetime.now()
		if args[0] == "Gwen":
			delta = datetime.datetime(2016, 6, 7) - datetime.datetime.now()
		if args[0] == "Jonas":
			delta = datetime.datetime(2016, 7, 18) - datetime.datetime.now()
		if args[0] == "Arne":
			delta = datetime.datetime(2016, 7, 30) - datetime.datetime.now()
		if args[0] == "Obi":
			delta = datetime.datetime(2016, 12, 2) - datetime.datetime.now()
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		reply = args[0] + " is jarig binnen " + str(days) + " dagen " + str(hours) + " uur " + str(minutes) + " minuten."
		self.send(kwargs['channel'], reply )


	def get_IM_channel(self, user):
		return json.loads(urllib.request.urlopen("https://slack.com/api/im.open?token=" + self.token + "&user=" + user). read().decode('utf-8'))["channel"]["id"]

	def send(self, channel, message, attachements=None):
		data =	{
					'token'			: self.token,
					'channel'		: channel,
					'type'			: 'message',
					'id'			: self.id,
					'text'			: message,
					'attachments'	: [] if attachements is None else attachements,
					'as_user'		: True
				}
		print(data)
		self.id = self.id + 1
		requests.post(self.message_link, data=data)

bot = MockupBot('xoxb-27973940390-ofTMTNyVAp9TYDg2hcpWsjxT')
bot.connect()
bot.get_channels()
t = threading.Thread(target=bot.ping)
t.start()
bot.run()