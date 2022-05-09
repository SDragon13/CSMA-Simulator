import random

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
			# print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, primary_channel)
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
				# print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
				if power + NOISE <= THRESHOLD:
					channels.append(channel)
		if(len(channels) == 4):
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
				# print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
				if power + NOISE <= THRESHOLD:
					if flag is False:
						flag = True
					channels.append(channel)
					continue
				if flag is True:	
					return channels
		if flag is True:
			return channels
	elif algorithm == 'Prob': #  Probabilistic 
		for channel in range(numOfChannel):
			power = 0
			if status == 'start':
				for n in nodes:
					if i == n.getID():
						continue
					else:
						power += n.getTXPower(channel)
				# print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
				if power + NOISE <= THRESHOLD:
					channels.append(channel)
		count = len(channels)
		if(count == 0):
			return [-1]
		retArr = []
		for i in range(count):
			flag = random.randint(1,i+1)
			if(flag == 1):
				retArr.append(channels[i])
		return retArr
	# filed with -1
	return [-1]
