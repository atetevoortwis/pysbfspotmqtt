import subprocess
import os
import paho.mqtt.publish as pub
import re
import logging, logging.handlers
import time
import pvoutput
import config
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
try:
    handler = logging.handlers.RotatingFileHandler('./sma.log', mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
    # create formatter
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

    # add formatter to ch
    handler.setFormatter(formatter)
    log.addHandler(handler)
except Exception as e:
    log.exception(e)

interval=10
mqtt = config.MQTT
sbfPath = config.SBF_PATH
sbfArgs = config.SBF_ARGS
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
#last PVOUTPUT:
lastPVOutput = None
while True:
    try:
        log.info("Running, sending to: %s:%s" % (mqtt['server'],mqtt['port']))
        if os.path.isfile(sbfPath):
            log.info('Running SBFSPOT')
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

        dataActual = {}
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
                #pub.single('sma/%s/value' % (tag+t), float(v),keepalive=60,hostname= mqtt['server'], port=mqtt['port'])
                dataActual[tag+t] = float(v)

        if lastPVOutput is None or time.time() - lastPVOutput > config.PVOUTPUT_INTERVAL:
            ts = time.localtime()
            lastPVOutput = time.time()
            data = {
                'd': "{:04}{:02}{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday),
                't': "{:02}:{:02}".format(ts.tm_hour, ts.tm_min),
                'v1': round(dataActual['EToday'] * 1000.),
                'v2': round(dataActual['Phase1ACPower'] * 1000.)
            }
            #pvoutput.doPVOutputRequest(data)
    except Exception as e:
        log.exception(e)
    time.sleep(interval)

