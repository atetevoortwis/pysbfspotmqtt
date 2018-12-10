
import subprocess
import os
import paho.mqtt.publish as pub
import re
import logging, logging.handlers
import time
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
try:
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    log.addHandler(handler)
except Exception as e:
    log.exception(e)

interval=10
mqtt = {'server': 'hass.local', 'port': 1883}
sbfPath = '/usr/local/bin/sbfspot.3/SBFspot'
sbfArgs = ['-v', '-nocsv' ,'-nosql','-finq']
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
while True:
    try:
        log.info("Running, sending to: %s:%s" % (mqtt['server'],mqtt['port']))
        if os.path.isfile(sbfPath):
            log('Running SBFSPOT')
            out = subprocess.Popen([sbfPath]+sbfArgs,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            stdout, stderr = out.communicate()

            data=stdout.decode('utf8')
        else:
            log.info('Running with test data')
            with open('data.txt') as f:
                data = f.readlines()
            mqtt = {'server': 'hass.local', 'port': 1883}
            data = ''.join(data)

        for tag, pat in patterns.items():
            if type(pat) is dict:
                r =re.search(pat['pattern'],data)
                tags = pat['tags']
            else:
                r = re.search(pat, data)
                tags = [tag]
                tag=''


            for v,t in zip(r.groups(),tags):
                log.info("Sending: %s: %s" % (tag+t,float(v)))
                pub.single('sma/%s/value' % (tag+t), float(v),keepalive=60,hostname= mqtt['server'], port=mqtt['port'])
    except Exception as e:
        log.exception(e)
    time.sleep(interval)

