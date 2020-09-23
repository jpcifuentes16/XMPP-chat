from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from xml.etree import cElementTree as ET
from sleekxmpp.plugins.xep_0004.stanza.field import FormField, FieldOption
from sleekxmpp.plugins.xep_0004.stanza.form import Form
from sleekxmpp.plugins.xep_0047.stream import IBBytestream

inbox={}
class Chat(object):
	def __init__(self):
		self.chat=[]
		self.untracked=[]

	def newMessage(self,user,message):
		self.chat.append(Message(user,message))
		self.untracked.append(Message(user,message))

	def printUntracked(self):
		for i in self.untracked:
			print(i.getMensaje())
		self.untracked=[]

	def isUntracked(self):
		return len(self.untracked)!=0

	def printChat(self):
		self.untracked=[]
		for i in self.chat:
			print(i.getMensaje())

	def printLastMessage(self):
		print(self.chat[-1].getMensaje())


class Message(object):
	def __init__(self,user,message):
		self.user=user
		self.message=message

	def getMensaje(self):
		return self.user+": "+self.message




class Cliente(ClientXMPP):

	def __init__(self, jid, password):

		ClientXMPP.__init__(self, jid, password)
		self.auto_authorize = True
		self.auto_subscribe = True

		self.add_event_handler("message", self.mensajeNuevo)

		self.register_plugin('xep_0030')
		self.register_plugin('xep_0004')
		self.register_plugin('xep_0066')
		self.register_plugin('xep_0077')
		self.register_plugin('xep_0050')
		self.register_plugin('xep_0047')
		self.register_plugin('xep_0231')
		self.register_plugin('xep_0045')
		self.register_plugin('xep_0095')  # Offer and accept a file transfer
		self.register_plugin('xep_0096')  # Request file transfer intermediate
		self.register_plugin('xep_0047')  # Bytestreams

		self['xep_0077'].force_registration = True
	
	def mensajeNuevo(self,msg):
		userFrom=str(msg['from'])
		#print(userFrom[:userFrom.find('/')])
		#print(userFrom[:userFrom.find('@')])
		#print(msg['body'])
		inbox[userFrom[:userFrom.find('/')]].newMessage(userFrom[:userFrom.find('@')],str(msg['body']))
		self.mensajes='nuevo Mensaje'
	
	def addSubscription(self,user):
		self.send_presence_subscription(pto=user,
										ptype='subscribe',
										pfrom=self.boundjid.bare)
					
	def updateInbox(self,user):
		if(user not in inbox):
			inbox[user]=Chat()
	
	def SendPresenceMessage(self,newPresence,newStatus):
		self.send_presence(pshow=newPresence, pstatus=newStatus)

	def updateInboxContacts(self):
		try:
			self.get_roster(block=True)
		except IqError as err:
			print('Error: %s' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		clientGroups = self.client_roster.groups()
		for group in clientGroups:
			for user in clientGroups[group]:
				
				# exclude the actual account
				if user == self.boundjid.bare:
					continue

				subscription = self.client_roster[user]['subscription']
				connections = self.client_roster.presence(user)

				# Get all users connected
				if connections.items():
					for platform, status in connections.items():
						self.updateInbox(user)
 

				# Get all users offline
				else:
					self.updateInbox(user)
	
	def getListOfContact(self):
		contactList=[]
		try:
			self.get_roster(block=True)
		except IqError as err:
			print('Error: %s' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		clientGroups = self.client_roster.groups()
		for group in clientGroups:
			for user in clientGroups[group]:
				
				# exclude the actual account
				if user == self.boundjid.bare:
					continue

				subscription = self.client_roster[user]['subscription']
				connections = self.client_roster.presence(user)

				# Get all users connected
				if connections.items():
					for platform, status in connections.items():	
						contactList.append(user)

				# Get all users offline
				else:
					contactList.append(user)
		return contactList

	def getContact(self,userSearch):
		try:
			self.get_roster(block=True)
		except IqError as err:
			print('Error: %s' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		clientGroups = self.client_roster.groups()
		for group in clientGroups:
			for user in clientGroups[group]:
				
				# exclude the actual account
				if user == self.boundjid.bare:
					continue

				subscription = self.client_roster[user]['subscription']
				connections = self.client_roster.presence(user)

				# Get all users connected
				if connections.items():
					for platform, status in connections.items():
						
						if status['show']:
							if(status['show']=='dnd'):
								status='busy'
							elif(status['show']=='xa'):
								status='Not available'
							else:
								status = status['show']
						else:
							status = 'available'

						if(userSearch==user):
							print()
							print(user)
							print('\t- Status: '+str(status))
							print('\t- Subscription: '+str(subscription))
							print('\t- Platform: '+str(platform))
							return 

				# Get all users offline
				else:
					if(userSearch==user):
						print()
						print(user)
						print('\t- Status: unavailable')
						print('\t- Subscription: '+str(subscription))
						break
		print('User not found!')
	
	
	def getMyContacts(self):
		try:
			self.get_roster(block=True)
		except IqError as err:
			print('Error: %s' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		clientGroups = self.client_roster.groups()
		for group in clientGroups:
			for user in clientGroups[group]:
				
				# exclude the actual account
				if user == self.boundjid.bare:
					continue

				subscription = self.client_roster[user]['subscription']
				connections = self.client_roster.presence(user)

				# Get all users connected
				if connections.items():
					for platform, status in connections.items():
						
						if status['show']:
							if(status['show']=='dnd'):
								status='busy'
							elif(status['show']=='xa'):
								status='Not available'
							else:
								status = status['show']
						else:
							status = 'available'

						print()
						print(user)
						print('\t- Status: '+str(status))
						print('\t- Subscription: '+str(subscription))
						print('\t- Platform: '+str(platform))

				# Get all users offline
				else:
					print()
					print(user)
					print('\t- Status: unavailable')
					print('\t- Subscription: '+str(subscription))
	
	def getAllUsers(self):
		# New form to the response
		formResponse = Form()
		formResponse.set_type('submit')

		formResponse.add_field(
			var='FORM_TYPE',
			ftype='hidden',
			type='hidden',
			value='jabber:iq:search'
		)

		formResponse.add_field(
			var='search',
			ftype='text-single',
			type='text-single',
			label='Search',
			required=True,
			value='*'
		)

		#Only define the username
		formResponse.add_field(
			var='Username',
			ftype='boolean',
			type='boolean',
			label='Username',
			value=1
		)
		# Create a iq to search using the form created
		search = self.Iq()
		search.set_type('set')
		search.set_to('search.'+self.boundjid.domain)
		search.set_from(self.boundjid.full)

		newQuery = ET.Element('{jabber:iq:search}query')
		newQuery.append(formResponse.xml)
		search.append(newQuery)
		results = search.send(now=True, block=True)

		# Convert the string result to structure
		results = ET.fromstring(str(results))
		ResultItems = []

		#Iterate the structure to get all the items
		for child in results:
			for node in child:
				for item in node:
					ResultItems.append(item)

		usersNames=[]
		# iterate the result items
		for item in ResultItems:
			for field in item.getchildren():
				try:
					if(field.attrib['var']=='Username'):
						usersNames.append(field.getchildren()[0].text)
				except:
					continue

		# order alphabetically all the user names
		sortedUserNames=sorted(usersNames, key=str.lower)
		for i in range(len(sortedUserNames)) :
			print(f'{i+1}. {sortedUserNames[i]}')

	def deleteAccount(self):
		resp = self.Iq()
		resp['type'] = 'set'
		resp['from'] = self.boundjid.full
		resp['register']['remove'] = True

		try:
			resp.send(now=True)
		except IqError as e:
			print('Could not unregister account: %s' %
						  e.iq['error']['text'])
			self.disconnect()
		except IqTimeout:
			print('No response from server.')
			self.disconnect()
	
	def enviarMensaje(self,contacto,mensaje):
		print('Enviar mensaje')
		self.sendMessage(mto=contacto,
						  mbody=mensaje,
						  mtype='chat')
	
	def desconectarse(self):
		# Using wait=True ensures that the send queue will be
		# emptied before ending the session.
		print('Entra al metodo')
		self.disconnect()
		print('Cierra sesion')

	def start(self):
		print('Start')
		self.send_presence()
		self.get_roster()

class RegisterClient(ClientXMPP):

	def __init__(self, jid, password):
		ClientXMPP.__init__(self, jid, password)

		# The session_start event will be triggered when
		# the bot establishes its connection with the server
		# and the XML streams are ready for use. We want to
		# listen for this event so that we we can initialize
		# our roster.
		self.add_event_handler("session_start", self.start, threaded=True)

		# The register event provides an Iq result stanza with
		# a registration form from the server. This may include
		# the basic registration fields, a data form, an
		# out-of-band URL, or any combination. For more advanced
		# cases, you will need to examine the fields provided
		# and respond accordingly. SleekXMPP provides plugins
		# for data forms and OOB links that will make that easier.
		self.add_event_handler("register", self.register, threaded=True)

	def start(self, event):
		self.send_presence()
		self.get_roster()

		# We're only concerned about registering, so nothing more to do here.
		self.disconnect()

	def register(self, iq):
		resp = self.Iq()
		resp['type'] = 'set'
		resp['register']['username'] = self.boundjid.user
		resp['register']['password'] = self.password

		try:
			resp.send(now=True)
			print("Account created for %s!" % self.boundjid)
		except IqError as e:
			print("Could not register account: %s" %
						  e.iq['error']['text'])
			self.disconnect()
		except IqTimeout:
			print("No response from server.")
			self.disconnect()