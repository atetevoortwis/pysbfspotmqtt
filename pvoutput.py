import requests
import logging
import config
import time
logger = logging.getLogger(__name__)
def doPVOutputRequest(data):
    logger.debug(data)

    headers = {
        'X-Pvoutput-Apikey': config.PVOUTPUT_APIKEY,
        'X-Pvoutput-SystemId': str(config.PVOUTPUT_SYSTEMID),
        'X-Rate-Limit': '1'
    }
    i = 0
    while i< config.PVOUTPUT_NTRY:
        try:
            r = requests.post(config.PVOUTPUT_URL, headers=headers, data=data, timeout=10)
            if 'X-Rate-Limit-Reset' in r.headers:
                reset = round(float(r.headers['X-Rate-Limit-Reset']) - time.time())
            else:
                reset = 0
            if 'X-Rate-Limit-Remaining' in r.headers:
                if int(r.headers['X-Rate-Limit-Remaining']) < 10:
                    logger.warning("Only {} requests left, reset after {} seconds".format(
                        r.headers['X-Rate-Limit-Remaining'],
                        reset))
            if r.status_code == 403:
                logger.warning("Forbidden: " + r.reason)
                logger.info("Sleeping for {}s".format(reset+1))
                time.sleep(reset + 1)
            else:
                r.raise_for_status()
                logger.info('Uploaded to PVOutput')
                break

        except requests.exceptions.RequestException as arg:
            logger.warning(arg)
            logger.info("Sleeping for {}s".format(i**3))
            time.sleep(i ** 3)
    else:
        logger.error("Failed to call PVOutput API")
if __name__ == '__main__':
    t = time.localtime()
    data = {
        'd': "{:04}{:02}{:02}".format(t.tm_year, t.tm_mon, t.tm_mday),
        't': "{:02}:{:02}".format(t.tm_hour, t.tm_min),
        'v1': round(0 * 1000),
        'v2': round(0)
    }
    doPVOutputRequest(data)
