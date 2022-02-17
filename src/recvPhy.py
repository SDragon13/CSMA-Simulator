def recvPhy(src,nodes,model,channel):
	msg = {'channel': channel,'txpower': []}
	count = 0
	for n in nodes:
		if n.getTXPower(channel) > 0:
			msg['txpower'].append(n.getTXPower(channel))
			count += 1
	print str(msg)
	if count != 1:
		return False
	else:
		return True
