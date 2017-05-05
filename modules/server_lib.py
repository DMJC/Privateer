import VS
import Director
import server
import launch
import dynamic_mission
import mission_lib
import guilds
import vsrandom
import universe
import faction_ships
import custom
import campaign_lib

def serverDirector():
	return server.getDirector()

def player_reinit(self):
	self.repair_bay_computer = None
	self.software_booth_computer = None
	self.computer_open=False

def player_docked_old(self):
	dynamic_mission.eraseExtras()
	dynamic_mission.plr = self.player_num
	dynamic_mission.fixerpct=0.0
	# dynamic_mission.guildpct=0.0
	for i in range(1):
		cursystem = VS.getSystemFile()
		syses = dynamic_mission.getSystemsNAway(cursystem,i,self.docked_un.getFactionName())
		for i in range(3):
			ind = vsrandom.randrange(0,len(syses))
			sys = syses[ind]
			print 'generating patrol'
			print sys
			dynamic_mission.generatePatrolMission(sys,vsrandom.randrange(4,10))
	for key in guilds.guilds:
		guild = guilds.guilds[key]
		if guild.HasJoined():
			guild.MakeMissions()

def player_docked(self):
	dynamic_mission.CreateMissions()
	print campaign_lib.getActiveCampaignNodes(-1)

def player_undocked(self):
	if not self.docked_un:
		print 'Base for'+self.callsign+'blew up!'
		return
	self.computer_open = False
	self.repair_bay_computer = None
	self.software_booth_computer = None

	dynamic_mission.eraseExtras()
	nam = self.docked_un.getName()
	
	campaign_lib.undock_campaigns()
	VS.IOmessage(0,'game','news',self.callsign+' has undocked from the '+nam)
	VS.IOmessage(0,'game','all',self.callsign+' has undocked from the '+nam)
	#self.objectives=1+VS.addObjective('Dock to the '+nam+' again')
	#VS.setCompleteness(self.objectives-1, -0.3)

def player_joined(self):
	self.sendMessage('Welcome, '+self.callsign+' to the server.')
	campaign_lib.resetCampaigns(self.player_num)

def player_execute(self):
	self.player_num=self.current_un.isPlayerStarship()

def server_execute(self):
	if (self.loopnum % 10000) == 0:
		pass
		#VS.IOmessage(0,"game","all","Howdy!  This server has run for "+str(self.loopnum)+" Python loops and has peaked at "+str(VS.getNumPlayers())+" players online!")



commandinfo = {
	"save": (1, "/save", "Saves your game."),
	"help": (0, "/help [command]", "Gives a list of commands or describes one."),
	"write": (1, "/write callsign text...", "Gives a personal message to callsign."),
	"userlist": (0, "/userlist", "Lists users in this starsystem"),
}
authcommandinfo = {
	"saveserver": (1, "/saveserver", "Saves server status"),
	"shiplist": (1, "/shiplist pagenum", "Lists all the ships available"),
	"launchme": (1, "/launchme ship [faction] [quantity]", "Launches a ship around yourself"),
	"launchtarg": (1, "/launchtarg ship [faction] [quantity]", "Launches a ship around your computer target"),
	"launch": (2, "/launch ship aroundship [faction] [quantity]", "Launches a ship around 'aroundship'"),
	"reload": (0, "/reload", "Reloads the server_lib.py file"),
	"setadmin": (2, "/setadmin callsign level", "Sets player either to have 1"),
	}

aliasinfo = {
	"message": "write", "whisper": "write",
	"shout": "say",
	"info": "help", "?": "help",
	"reload2": "reload",
	}

def getCommandInfo(command, auth=True):
	if command in aliasinfo:
		command = aliasinfo[command]
	cmdinfo=None
	if auth>=1 and command in authcommandinfo:
		cmdinfo = authcommandinfo[command]
	elif command in commandinfo:
		cmdinfo = commandinfo[command]
	return cmdinfo

def processMessage(player, auth, command, args, id=''):
	if command in aliasinfo:
		command = aliasinfo[command]
	#cmdinfo = getCommandInfo(command, auth)
	if auth<1 and command in authcommandinfo:
		player.sendMessage("#884400You must be authorized to use "+command)
		return
	#if cmdinfo and len(args)<cmdinfo[0]:
	#	processMessage(player,True,"help",[command])
	#	return
	if command=='help':
		if len(args)<1:
			cmdstr = '#8800cc'+' '.join(commandinfo)
			if auth>=1:
				cmdstr += '#cc0088 '+' '.join(authcommandinfo)
			player.sendMessage('#888800Valid commands: '+cmdstr)
		else:
			cmdinfo = getCommandInfo(args[0], True)
			if cmdinfo and len(cmdinfo)>=3:
				player.sendMessage("#888800Usage: #880088"+cmdinfo[1]+"#888800 - "+cmdinfo[2])
			else:
				player.sendMessage("#884400/"+args[0]+" does not exist. Use /help for a list of commands.")
	elif command=='reload':
		if auth<1:
			return
		vsmod=VS
		reload(__import__('server_lib'))
		vsmod.IOmessage(0,"game","all","The server python script has been reloaded.")
	elif command=='userlist':
		cstr = '#44cc44Users on the server:#888800'
		print len(serverDirector().playerlist)
		for x in serverDirector().playerlist:
			#print x
			#print x.callsign
			if x.callsign:
				cstr += ' '+x.callsign
		player.sendMessage(cstr)
	elif command=='shiplist':
		cnt=0
		min=-1
		max=-1
		cstr=''
		if 1: #try:
			page=int(args[0])
			cstr = '#44cc44Available ships (#888800'+str(page)+'#44cc44):#888800'
			num=10
			min=(page-1)*num
			max=page*num
		else: #except:
			min=-1
		if min<0:
			processMessage(player,False,"help",[command])
		else:
			shiplist=faction_ships.stattableexp.keys()
			shiplist.sort()
			for x in shiplist:
				cnt+=1
				if cnt>=min and cnt<max:
					cstr+= ' '+x
			player.sendMessage(cstr)
	elif command=='launcheach':
		if auth<1:
			return
		shiplist = faction_ships.stattableexp.keys()
		for x in shiplist:
			processMessage(player,1,"launchme",[x])
	elif command=='save':
		VS.saveGame(str(player.player_num))
	elif command=='saveserver' and auth>=1:
		VS.saveGame('0')
	elif command=='setadmin':
		if len(args)<2:
			return
		if auth<1:
			return
		playerto = serverDirector().getPlayerByCallsign(args[0])
		if not playerto:
			print args[0]
			player.sendMessage("#884400Cannot find player "+args[0])
			return
		print args
		value=0.0
		if args[1]=='yes' or args[1]=='1':
			value=1.0
		pnum=playerto.player_num
		if Director.getSaveDataLength(pnum, 'serveradmin')<1:
			Director.pushSaveData(pnum, 'serveradmin', value)
		else:
			Director.putSaveData(pnum, 'serveradmin', 0, value)
		playerto.sendMessage("Your admin status set to "+str(value))
	elif command=='write':
		if len(args)<1:
			return
		playerto = serverDirector().getPlayerByCallsign(args[0])
		if not playerto:
			player.sendMessage("#884400Cannot find player "+args[0])
			return
		playerto.sendMessage(' '.join(args[1:]), player.callsign)
		player.sendMessage('Message to '+args[0]+': '+(' '.join(args[1:])))
	elif command=='say':
		VS.IOmessage(0, player.callsign,'all',' '.join(args))
	elif command=='launchme' or command=='launchtarg' or command=='launch':
		if auth<1:
			return
		if len(args)<1:
			return
		factquan=()
		if command=="launchtarg" or command=="launchme":
			if not player.current_un:
				player.sendMessage("#884400Use /launch <unit> <aroundname> to launch when you are null.")
				return
			if len(args)>=3:
				factquan=(args[1],args[2])
			elif len(args)>=2:
				factquan=(args[1],)
			targun = player.current_un
			if command=="launchtarg":
				metarg=targun.GetTarget()
				if metarg:
					targun = metarg
		else:
			if len(args)<2:
				processMessage(player,False,"help",[command])
				return
			if len(args)>=4:
				factquan=(args[2],args[3])
			elif len(args)>=3:
				factquan=(args[2],)
			targunname = args[1].lower()
			iter = VS.getUnitList()
			while not iter.isDone():
				targun=iter.current()
				if targun.getName().lower()==targunname:
					break
				if targun.getFullname().lower()==targunname:
					break
				iter.advance()
		faction = targun.getFactionName()
		type=args[0]
		quantity=1
		for a in factquan:
			try:
				int(a)
				quantity=int(a)
				print quantity
			except ValueError:
				faction=a
				print faction
		fgname='AI'
		ainame='default'
		launch.launch_wave_around_unit(fgname,faction,type,ainame,quantity,2000.0,4000.0,targun)
	else:
		processMessage(player, auth, "help", [command])

