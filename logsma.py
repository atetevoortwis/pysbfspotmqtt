with open('data.txt') as f:
    data = f.readlines()
mqtt = {'server': 'hass.local','port':1883}
data = ''.join(data)

import paho.mqtt.publish as pub
import re

patterns = {
    'EToday': r'EToday: (.*)kWh',
    'ETotal': r'ETotal: (.*)kWh',
    'OperationTime': r'Operation Time: (.*)h',
    'FeedInTime': r'Feed-In Time  : (.*)h',
    'String1DC': {'pattern': r'String 1 Pdc:   (.*)kW - Udc: (.*)V - Idc:  (.*)A',
                'tags': ['Power','Voltage','Current']},
    'String2DC': {'pattern': r'String 2 Pdc:   (.*)kW - Udc: (.*)V - Idc:  (.*)A',
                'tags': ['Power','Voltage','Current']},
    'Phase1AC': {'pattern': r'Phase 1 Pac :  (.*)kW - Uac: (.*)V - Iac:  (.*)A',
                'tags': ['Power','Voltage','Current']},
}
for tag, pat in patterns.items():
    if type(pat) is dict:
        r =re.search(pat['pattern'],data)
        tags = pat['tags']
    else:
        r = re.search(pat, data)
        tags = [tag]
        tag=''


    for v,t in zip(r.groups(),tags):
        print('%s: %s' % (tag+t,float(v)))

        pub.single('sma/%s/value' % (tag+t), float(v),keepalive=60,hostname= mqtt['server'], port=mqtt['port'])

