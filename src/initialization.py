from Source import Source
from event import event


def initialization(t,src,n,createTime):
	argv = {}
	argv['time'] = t
	argv['actType'] = 'sendMac'
	argv['src'] = src
	argv['des'] = n - 1
	argv['pacSize'] = 60
	argv['pacData'] = src
	argv['pacType'] = 'data'
	argv['pacAckReq'] = True
	argv['channel'] = []
	argv['createTime'] = createTime
	argv['arriveTime'] = -1
	e = event(argv)
	return e

