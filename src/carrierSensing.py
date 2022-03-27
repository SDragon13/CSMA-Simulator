
# Only Primary

def carrierSensingOP(i, status, nodes, numOfChannel=2):
	primary_channel = 0  # default 0 is the primarry channel
	NOISE = 0.2
	THRESHOLD = 0.2  # for the time being
	channels = []
	power = 0
	if status == 'start':
		for n in nodes:
			if i == n.getID():
				continue
			else:
				power += n.getTXPower(primary_channel)
		print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
		if power + NOISE <= THRESHOLD:
			channels.append(primary_channel)
			return channels
	return [-1]


#  SCB
def carrierSensing(i, status, nodes, numOfChannel=2, algorithm='OP'):
	NOISE = 0.2
	THRESHOLD = 0.2  # for the time being
	channels = []
		
	if algorithm == 'OP':	#  Only Primary
		power = 0
		primary_channel = 0
		if status == 'start':
			for n in nodes:
				if i == n.getID():
					continue
				else:
					power += n.getTXPower(primary_channel)
			print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, primary_channel)
			if power + NOISE <= THRESHOLD:
				channels.append(primary_channel)
				return channels
	elif algorithm == 'SCB': # 
		for channel in range(numOfChannel):
			power = 0
			if status == 'start':
				for n in nodes:
					if i == n.getID():
						continue
					else:
						power += n.getTXPower(channel)
				print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
				if power + NOISE <= THRESHOLD:
					channels.append(channel)
					return channels
	elif algorithm == 'AM': #  alway max 
		flag = False
		for channel in range(numOfChannel):
			power = 0
			if status == 'start':
				for n in nodes:
					if i == n.getID():
						continue
					else:
						power += n.getTXPower(channel)
				print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
				if power + NOISE <= THRESHOLD:
					if flag is False:
						flag = True
					channels.append(channel)
					continue
				if flag is True:	
					return channels
		if flag is True:
			print(channels)
			return channels
	# filed with -1
	return [-1]
