import smamodbus
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

sma = smamodbus.SMAModbus(config.MODBUS_URL,config.MODBUS_UNIT_ID)

#last PVOUTPUT:
lastPVOutput = None
while True:
    try:
        log.info("Running, sending to: %s:%s" % (mqtt['server'],mqtt['port']))

        dataActual = sma.readModbus()
        for tag,v in dataActual.items():
            log.info("Sending: %s: %s" % (tag,float(v)))
            pub.single('sma/%s/value' % tag, float(v),keepalive=60,hostname= mqtt['server'], port=mqtt['port'])
            dataActual[tag] = float(v)

        if lastPVOutput is None or time.time() - lastPVOutput > config.PVOUTPUT_INTERVAL:
            ts = time.localtime()
            lastPVOutput = time.time()
            data = {
                'd': "{:04}{:02}{:02}".format(ts.tm_year, ts.tm_mon, ts.tm_mday),
                't': "{:02}:{:02}".format(ts.tm_hour, ts.tm_min),
                'v1': round(dataActual['EToday'] * 1000.),
                'v2': round(dataActual['Phase1ACPower'] * 1000.)
            }
            print(data)
            if dataActual['ETotal']>0.:
                #only send if no false zeros TODO: Fix this, how to check?
                pvoutput.doPVOutputRequest(data)
                pass
    except Exception as e:
        log.exception(e)
    time.sleep(interval)

