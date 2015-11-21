#!/usr/bin/env python

import requests
import logging
from logging.handlers import TimedRotatingFileHandler

API_TOKEN='xxxx'
LOG_FILENAME = '/var/log/rundeck_takeover.log'
PORT= '443'
RUNDECK_SERVERS = {'https://rundeck1.mycompany.com': 'RUNDECK1-UUID-UUID-UUID-UUIDUUIDUUID',
                   'https://rundeck2.mycompany.com': 'RUNDECK2-UUID-UUID-UUID-UUIDUUIDUUID',
                   'https://rundeck3.mycompany.com': 'RUNDECK3-UUID-UUID-UUID-UUIDUUIDUUID'
                  }


def config_log(log_filename):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(log_filename, when="d", interval=30, backupCount=5)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def health_check(rundeckserver):
    """
    Return True if the given Rundeck server is up and running

    param: rundeckserver Server name
    """
    url = "%s:%s/api/1/system/info" % (rundeckserver, PORT)
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_TOKEN }
    try:
        r = requests.put(url, headers=headers)
        if r.status_code == requests.codes.ok:
                return True
    except requests.exceptions.RequestException:
        return False
    return False


def takeover_schedule_jobs(rundeckserver, server_uuid):
    """
    Takeover scheduled jobs from affected servers

   :param rundeckserver: rundeck server that takes over
   :param server_uuid: server UUID to take over from
    """
    url = '%s:%s/api/14/scheduler/takeover' % (rundeckserver, PORT)
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_TOKEN }
    payload = "{ server: { uuid: \""+ server_uuid +"\" } }"
    r = requests.put(url, headers=headers, data=payload)
    if r.status_code != requests.codes.ok:
        raise Exception("%s server failed to takeover from %s" % (rundeckserver, server_uuid))


def main_takeover():
    affected_servers = []
    healthy_server = None

    for server in RUNDECK_SERVERS:
        if health_check(server):
            healthy_server = server
        else:
            affected_servers.append(server)

    if len(affected_servers) == 0:
        logger.info("There are no Rundeck servers affected :-)")

    elif not healthy_server:
        logger.error("There is no Rundeck server available :-(")

    else:
        try:
            logger.info("List of affected servers: %s" % ', '.join(affected_servers))
            for affected in affected_servers:
                logger.info("%s will take over %s's scheduled jobs..." % (healthy_server, affected))
                takeover_schedule_jobs(healthy_server, RUNDECK_SERVERS[affected])
                logger.info("Done")
        except Exception, err:
            logger.error(err)


if __name__ == "__main__":
    try:
        logger = config_log(LOG_FILENAME)
        main_takeover()
    except Exception, e:
        logger.error(e)
