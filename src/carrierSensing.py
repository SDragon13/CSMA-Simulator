

def carrierSensing(i, status, nodes, numOfChannel=2):
	NOISE = 0.2
	THRESHOLD = 0.2  # for the time being
	channels = []
    # add more channels
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

		elif status == 'end':
			print nodes[i].getCCAResult()
			for key in nodes[i].getCCAResult():
				power += nodes[i].getCCAResult()[key][channel]
			print 'power: %s, noise: %s, THRESHOLD: %s, channel: %s' % (power, NOISE, THRESHOLD, channel)
			if power + NOISE <= THRESHOLD:
				return channels
	# filed with -1
	return -1
