#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cProfile import label
from glob import glob
from multiprocessing import Value
from Source import Source
from action import action
import operator
import random
from event import event
from initialization import initialization
import csv
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['STZhongsong']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题


from aoi import AOI,Freshness,allEventMap,collision,channel_count

def runSimulation(number, numOfChannel, dcb):
	numOfNodes = number+1

	nodes = []

	for i in range(numOfNodes):  # initialize nodes
		argv = {}
		argv['ID'] = i
		argv['src'] = i
		argv['des'] = numOfNodes - 1
		n = Source(argv)
		n.initCCAResult(numOfNodes, numOfChannel)
		nodes.append(n)
		global AOI
		AOI[i] = [] # each node has AOI list for each package
		global Freshness
		Freshness[i] = [] # Freashness 
		collision[i] = 0 # record how much collision happen
		channel_count[i] = 0 # record how much channel used in transport

	eventList = []
	global allEventMap
 
	for i in range(numOfNodes-1):
		# t = random.randint(10, 100)*20
		t = 0 # all nodes start capture in 0 s
		e = initialization(t, i, numOfNodes,t)
		eventList.append(e)
		allEventMap[i] = []
	
	for i in range(numOfNodes-1):
		t = eventList[i].time
		for j in range(20):
			t += 3000	# us
			e = initialization(t, i, numOfNodes,t)
			allEventMap[i].append(e)
	for i in range(len(allEventMap[0])):
		print allEventMap[0][i].__dict__
	
	while True:
		if not eventList:
			break
		else:
			min_index, min_t = min(enumerate(e.time for e in eventList),key=operator.itemgetter(1))	# find next event
			newList = action(eventList[min_index], nodes, 'normal', numOfChannel, dcb)
			eventList.pop(min_index)   # delete which is handled
			for n in newList:
				eventList.append(n)
    
	print('RES:', AOI)
	print('collision', collision)
	count = 0
	for item in collision.values():
		count += item
	print('avg collision', count/number)
	print('channel_count', channel_count)
	count = 0
	for item in channel_count.values():
		count += item
	print('avg channel_count', 1.0*count/number/21)
	avg_aoi =	draw(dcb)
	return avg_aoi

def draw(dcb):
	matplotlib.rcParams['xtick.labelsize'] = 8
	matplotlib.rcParams['ytick.labelsize'] = 8
	matplotlib.rcParams['axes.labelsize'] = 8
	avg_aoi = []
	for index in range(len(AOI.keys())-1):
		res = AOI[index]
		if len(res) == 0:
			break
		x = [0]
		y = [0]
		create_time = 0
		arrive_time = 0
		res.pop(-1)
		res.pop(-1)
		for value in res:
			x.append(value['arrive'])
			x.append(value['arrive'])
			height = value['arrive'] - create_time
			low = value['arrive'] - value['create']
			y.append(height)
			y.append(low)
			create_time = value['create']
		x = [float(i)/1000 for i in x]
		y = [float(i)/1000 for i in y]
		# print x,y
		# l = plt.plot(x, y, label='STA%s' % index)
		path = './'
		title = ''
		if dcb == 'SCB':
			title = 'Static Channel Bonding'
			path += 'scbres'
		elif dcb == 'OP':
			title = 'Only Primary'
			path += 'opres'
		elif dcb == 'AM':
			title = 'Always Max'
			path += 'amres'
		elif dcb == 'Prob':
			title = 'Probabilistic Uniform'
			path += 'pbres'
		plt.title(title)
		font2 = {'family' : 'Times New Roman',
			'weight' : 'normal',
			'size'   : 15,
		}
		# plt.xlabel('Time/ms', font2)
		# plt.ylabel('AoI/ms', font2)
		# plt.legend(loc="upper left")
		# plt.savefig('%s/node%s.png' % (path,index))
		# plt.show()
		area = 0
		x1 = 0
		x2 = 0
		xlen = len(x)
		i = 0
		while(i+2<=xlen):
			x1 = x[i]
			x2 = x[i+1]
			y1 = y[i]
			y2 = y[i+1]
			tmp = 1.0*(y1+y2)*(x2-x1)/2
			area += tmp
			i = i+2
		avg_aoi.append(1.0*area/x[xlen-1])
	ret = np.mean(avg_aoi)
	print 'avg_aoi',avg_aoi
	print 'avg_aoi',ret
	return ret

def fromSecondToSlot(second):
	return second*250000/4


def fromSlotToSecond(slot):
	return slot*4/250000


dcb = 'Prob'
res = []
# runSimulation(8 ,4, dcb) # AM | OP | SCB | Prob
plt.cla() 
matplotlib.rcParams['xtick.labelsize'] = 8
matplotlib.rcParams['ytick.labelsize'] = 8
matplotlib.rcParams['axes.labelsize'] = 8
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
dcbArr = ['OP', 'SCB', 'AM', 'Prob']
for dcb in dcbArr:
	y1 = runSimulation(4 ,4, dcb) # AM | OP | SCB | Prob
	y2 = runSimulation(8 ,4, dcb) # AM | OP | SCB | Prob
	y3 = runSimulation(16 ,4, dcb) # AM | OP | SCB | Prob
	y4 = runSimulation(32 ,4, dcb) # AM | OP | SCB | Prob
	y5 = runSimulation(64 ,4, dcb) # AM | OP | SCB | Prob
	title = 'Average Age for Different User Counts'
	if dcb == 'SCB':
		title = 'Static Channel Bonding'
	elif dcb == 'OP':
		title = 'Only Primary'
	elif dcb == 'AM':
		title = 'Always Max'
	elif dcb == 'Prob':
		title = 'Probabilistic Uniform'
	x = [4,8,16,32,64]
	y = [y1,y2,y3,y4,y5]
	res.append(y)
	# x = [4,8]
	# y = [y1,y2]
	x = [float(i) for i in x]
	y = [float(i) for i in y]
	# l = plt.plot(x, y,label=title)
	# plt.title('')
	# font2 = {'family' : 'Times New Roman',
	# 	'weight' : 'normal',
	# 	'size'   : 15,
	# }
	# plt.xlabel("Number of Users", font2)
	# plt.ylabel("Average AoI/ms", font2)	
	# plt.legend()
	# plt.savefig('%s/all.png' % ('./aoires'))
	# plt.show()
print 'res:',res
