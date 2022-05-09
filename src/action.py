from event import event
import random
from Source import Source
import sys
import copy
from carrierSensing import carrierSensing
from recvPhy import recvPhy
from initialization import initialization
import math

from aoi import AOI, T, Freshness, allEventMap,collision,channel_count

METHOD = '802.15.4'
TRAFFIC_SATURATED = False

phy_time = 1000

def action(curEvent,nodes,mode,numOfChannel,dcb):

	DEBUG = True

	BACKOFF_PERIOD = 20
	CCA_TIME = 8
	TX_TURNAROUND = 12
	ACK_TIME = 0  #12
	TX_TIME_ACK = 19  #22

#	pacInterval = random.randint(pacInterval - 100,pacInterval + 100)
	arg = curEvent.actType
	i = curEvent.src
	t = curEvent.time
	des = curEvent.des
	channels = curEvent.channel

	newList = []
	nodes[i].updateEnergy(t)

	if arg == 'sendMac':
		# add cca to check if channel is idle?
		channel = carrierSensing(i, 'start', nodes, numOfChannel, dcb) # [channel1, channel2...]
		if channel[0] == -1:
			new = copy.copy(curEvent)
			new.time = t + CCA_TIME 
			new.actType = 'sendMac'
			newList.append(new)
			collision[i] = collision[i] + 1
			return newList
		#nodes[i].updateEnergy(t)
		nodes[i].setPower('idle')

		new = copy.copy(curEvent)
		new.time = t
		new.actType = 'backoffStart'
		newList.append(new)

		nodes[i].timeStamping(t,'start')  # record the start of a packet

		if not DEBUG:
			print 'node:', nodes[i].ID, nodes[i].getChannelIndicators()

		if DEBUG:
			print 'node:', t, nodes[i].ID, 'send mac'

	elif arg == 'backoffStart':
		# the start of the WHOLE backoff process, boCount = 0

		nodes[i].setPower('sleep') # power lever = 1
		nodes[i].setCW(1)  # -1 or value
		nodes[i].setBOCount(0) # 0 or 1

		# 802.15.4 backoff
		if METHOD == '802.15.4':
			minBE, maxBE = nodes[i].getBE()
			nodes[i].setBOExponent(minBE)

		new = copy.copy(curEvent)
		new.time = t
		new.actType = 'backoff'
		newList.append(new)

		if DEBUG:
			print 'node:',t, nodes[i].ID, 'backoff start.'

	elif arg == 'backoff':

		nodes[i].setPower('sleep')
		new = copy.copy(curEvent)
		# 802.15.4 backoff
		if METHOD == '802.15.4':
			tmp = random.randint(0, 2**nodes[i].getBOExponent()-1)
		new.time = t + tmp*BACKOFF_PERIOD
		new.actType = 'ccaStart'
		newList.append(new)

		if DEBUG:
			print 'node:', t, nodes[i].ID, 'backoff'

	elif arg == 'ccaStart':

		nodes[i].setPower('sense') # power lever = 20
		channel = carrierSensing(i, 'start', nodes, numOfChannel, dcb) # [channel1, channel2...]

		if channel[0] != -1:
		#	print 'channel start is idle'
			channel_count[i] = channel_count[i] + len(channel)
			new = copy.copy(curEvent)
			new.time = t + CCA_TIME # CCA_TIME = 8
			new.actType = 'ccaEnd'
			new.channel = channel
			# TODO(use range to each channel)
			# nodes[i].setCCA(0, channel[0])
			nodes[i].setTXPower(5, channel[0])
			newList.append(new)
   
			if DEBUG:
				print 'node:', t, nodes[i].ID, 'CCA starts. channel:', channel 

		else:
			# channel is busy
			#print 'channel start is busy'
			new = copy.copy(curEvent)
			new.time = t + CCA_TIME
			new.actType = 'ccaEnd'
			nodes[i].setCCA(1, channel[0])
			newList.append(new)

			if DEBUG:
				print 'node:', t, nodes[i].ID, 'channel busy.'

	elif arg == 'ccaEnd':
		nodes[i].setPower('idle')
		channel = channels
		if len(channel) != 0 and channel[0] != -1:
			#print 'channel end is idle'
			nodes[i].setCW(-1)
			if nodes[i].getCW() == 0:
				# channel is idle for 2 consecutive CCA
				nodes[i].updateBOStat('idle')
				new = copy.copy(curEvent)
				new.time = t + TX_TURNAROUND # 12
				new.actType = 'sendPhy'
				newList.append(new)
				nodes[i].setCW(2)
				if DEBUG:
					print 'node:', t, nodes[i].ID, 'channel is confirmed idle. channel:', channel  

			else:
				new = copy.copy(curEvent)
				new.time = t + TX_TURNAROUND # 12
				new.actType = 'ccaStart'
				newList.append(new)

				if DEBUG:
					print 'node:',t, nodes[i].ID, 'channel is idle for 1 slot, sense for another.'

		else:
			#print 'channel end is busy'
			#channel is busy
			nodes[i].setBOCount(1)
			nodes[i].updateBOStat('busy')

			if METHOD == '802.15.4':
				minBE, maxBE = nodes[i].getBE()
				nodes[i].setBOExponent(min(nodes[i].getBOExponent()+1, maxBE))

			if nodes[i].getBOCount() > nodes[i].getBOLimit():
				# for now assume that the interval between 2 packets is large enough
				# so no need to consider other packets in queue
				# return an empty list to indicate mission ending.
			#print  nodes[i].getBOCount()
			#print 'Exceeds backoff limit...'

				nodes[i].timeStamping(t, 'end')    # can add 100000000 to indicate failure.
				#nodes[i].timeStamping(nodes[i].getPacStart()+nodes[i].getPacInterval(),'end')  # use pac interval as the max delay
				# schedule new packet transmission.

				temp = nodes[i].getPacInterval()
				nodes[i].insertPastInterval(temp)

				nextPacket(mode, nodes, newList, i, t, temp, curEvent.createTime) # debug


				nodes[i].updateDelayStat()
				nodes[i].updatePacStat(0)
				# added just to see the effect
				nodes[i].updateTRYStat('fail')
				nodes[i].setBOCount(0)
				nodes[i].setRTCount(0)

				if DEBUG:
					print 'node:', t, nodes[i].ID, 'channel busy, exceeds backoff limit..'

			else:
				#new = event(curEvent)
				new = copy.copy(curEvent)
				new.time = t + TX_TURNAROUND # 12
				new.actType = 'backoff'
				newList.append(new)
				# nodes[i].setCCA(0, channel[0])

				if DEBUG:
					print 'node:', t, nodes[i].ID, 'channel busy, performs backoff.'

	elif arg == 'sendPhy':
		nodes[i].setPower('tx')
		if curEvent.pacType == 'data':
      		#update the power, add channel param
			for channel in channels:
				nodes[i].setTXPower(5, channel)

			print 'after setTXPower'
			print nodes[i].getTXPower(channels[0])
   			# tx_time = TX_TIME_DATA
			if t < fromSecondToSlot(100):
				tx_time = nodes[i].getTxTime(channels[0])
			elif t< fromSecondToSlot(300):
				tx_time = nodes[i].getTxTime(channels[0]) + 20
			elif t< fromSecondToSlot(400):
				tx_time = nodes[i].getTxTime(channels[0]) + 40
			else:
				tx_time = nodes[i].getTxTime(channels[0])
			tx_time = tx_time * len(channels)
		elif curEvent.pacType == 'ack':
			print 'in ack, none setTXPower'
			tx_time = TX_TIME_ACK
		else:
			print 'no such tx time....'
			sys.exit(0)

		nodes[i].setPower('tx')
		new1 = copy.copy(curEvent)
		new1.src = des
		new1.des = i
		new1.actType = 'recvPhy'
		new1.time = t + tx_time
		newList.append(new1)

		new2 = copy.copy(curEvent)
		new2.time = t + tx_time
		new2.actType = 'sendPhyFinish'
		newList.append(new2)

		if DEBUG:
			print 'node:', t, nodes[i].ID, 'send phy.'

	elif arg == 'sendPhyFinish':
	# set up the transmitter.
		# channel = channels
		nodes[i].setPower('sleep')
		for channel in channels:
			nodes[i].setTXPower(0, channel)
		nodes[i].setPower('rx')
		
		if DEBUG:
			print 'node:', t, nodes[i].ID, 'send phy finished.'


	elif arg == 'timeoutAck':

		nodes[i].setPower('sleep')
		nodes[i].setRTCount(1)
		nodes[i].updateTRYStat('fail')
		if nodes[i].getRTCount() > nodes[i].getRTLimit():
			#transmission failed.
			#print arg,'Exceed retry limit....'
			nodes[i].timeStamping(t, 'end')
			# schedule new packet transmission
			temp = nodes[i].getPacInterval()
			nodes[i].insertPastInterval(temp)
			nextPacket(mode, nodes, newList, i, t, temp, curEvent.createTime) # debug

			'''
			if mode == 'node increase':
				new = initPacket(nodes[i].getPacStart()+random.randint(temp-1,temp+1),i,len(nodes))
				newList.append(new)
			elif mode == 'node decrease':
				if i <= 5 or t <= 300000:
					new = initPacket(nodes[i].getPacStart()+random.randint(temp-1,temp+1),i,len(nodes))
					newList.append(new)
				else:
					nodes[i].setPacInterval(0)
			'''

			nodes[i].updateDelayStat()
			nodes[i].updatePacStat(0)
			nodes[i].setBOCount(0)
			nodes[i].setRTCount(0)

			if DEBUG:
				print 'node:', t, nodes[i].ID, 'ACK time out. Exceeds retry limit'

		else:
			#print arg,'packet collision'
			new = copy.copy(curEvent)
			new.actType = 'backoffStart'
			new.time = t
			newList.append(new)

			if DEBUG:
				print 'node:',t, nodes[i].ID, 'ACK time out. Performs a new try.'



	elif arg == 'recvPhy':
		# channel = channels
		nodes[i].setPower('rx')
		model = 'ch_model'
		probRecv = True
		for channel in channels:
			recvPhy(i, nodes, model, channel) # determine if all packets have arrived 
		#print probRecv, curEvent.pacType,nodes[i].BOCount,i
		if probRecv:
			if curEvent.pacType == 'ack':
				new = copy.copy(curEvent)
				new.time = t + phy_time / len(channels)
				new.actType = 'recvMac'
				newList.append(new)

				if DEBUG:
					print 'node:',t, nodes[i].ID, 'received ACK at PHY.'

			else:
				nodes[i].setTXPower(5, channels[0]) # one channel back
				new = copy.copy(curEvent)
				new.time = t + phy_time / len(channels)
				new.actType = 'recvMac'
				newList.append(new)

				if DEBUG:
					print 'node:',t, nodes[i].ID, 'received data at PHY.'
		else:
			if curEvent.pacType == 'ack':
				# nodes failed to receive ack.
				new = copy.copy(curEvent)
				new.time = t
				new.actType = 'timeoutAck'
				newList.append(new)

				if DEBUG:
					print 'node:',t, nodes[i].ID, 'failed to receive ACK.'

			elif curEvent.pacType == 'data':
				new = copy.copy(curEvent)
				new.time = t
				new.src = des
				new.des = i
				new.actType = 'timeoutAck'
				newList.append(new)

				if DEBUG:
					print 'node:',t, nodes[i].ID, 'failed to receive data.'

	elif arg == 'recvMac':
		nodes[i].setPower('idle')
		if curEvent.pacType == 'data':
			if curEvent.pacAckReq:
				new = copy.copy(curEvent)
				new.time = t + ACK_TIME  # t_ack
				new.arriveTime = t # package arrive time
				if new.des == 0:
					print new.arriveTime
				new.actType = 'sendPhy'
				new.pacType = 'ack'
				new.pacAckReq = False
				# need check the following
				new.des = curEvent.des
				new.src = curEvent.src
				print 'recvMax: src: %s, des: %s' % (new.src, new.des)
				# here can mark the receiving of the data
				newList.append(new)
		
				if DEBUG:
					print 'node:',t, nodes[i].ID, 'received data at MAC. prepare to send an ACK.'

		elif curEvent.pacType == 'ack':
			# packet successfully sent and recieve right ack
			nodes[i].updateTRYStat('suc')
			nodes[i].timeStamping(t,'end')
			# to schedule next packet transmission. When t is small, channel indicators are not stable.

			temp = nodes[i].getPacInterval()
			nodes[i].insertPastInterval(temp)
			# nextPacket(mode, nodes, newList, i, t, temp) # init packet in run.py in 2022/4/10
			global allEventMap
			if len(allEventMap[i]) > 0:
				event = allEventMap[i].pop(0)
				if event.createTime < t: 
					event.time = t	# next packet start
				newList.append(event)

			nodes[i].updateDelayStat()
			nodes[i].updatePacStat(1)
			nodes[i].setRTCount(0)
			nodes[i].setBOCount(0)
			
			# curEvent.arriveTime = t
			print('successful event: ', curEvent.__dict__)
			# event_aoi = curEvent.arriveTime - curEvent.createTime
			event_aoi = {
				'create': curEvent.createTime,
       			'arrive': curEvent.arriveTime,
            }
			if curEvent.arriveTime < curEvent.createTime:
				print curEvent.__dict__
			global AOI
			AOI[i].append(event_aoi)
			global Freshness
			# pack_freshness = '%.2f'%((T-event_aoi['create']) * 1.0 / T)
			# Freshness[i].append(pack_freshness)
			if DEBUG:
					print 'node:', t, nodes[i].ID, 'received data at MAC. Packet Succeed.'


	return newList


def nextPacket(mode, nodes, newList, i, t, temp, createTime):
	if not TRAFFIC_SATURATED:
		if mode == 'node increase' or mode == 'normal':
			if t < fromSecondToSlot(200) or t > fromSecondToSlot(400):
				temp = random.randint(math.floor(temp*0.9), math.floor(temp*1.1))*20
			else:
				temp = random.randint(math.floor(temp*0.9*0.5), math.floor(temp*1.1*0.5))*20

			new = initialization(nodes[i].getPacStart()+temp, i, len(nodes), createTime)
			newList.append(new)
		elif mode == 'node decrease':
			if i < 30 or t <= fromSecondToSlot(50):
				new = initialization(nodes[i].getPacStart()+random.randint(temp-1, temp+1), i, len(nodes), createTime)
				newList.append(new)
			else:
				nodes[i].setPacInterval(fromSecondToSlot(50))
	else:
		new = initialization(t+(20-t%20), i, len(nodes), createTime)
		newList.append(new)

def fromSecondToSlot(second):
	return second*250000/4
