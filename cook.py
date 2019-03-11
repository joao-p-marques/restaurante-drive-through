# coding: utf-8

import logging
import pickle
import zmq
from utils import work, REQ_TASK, TASK_READY

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def main(ip, port):
    # create a logger for the client
    logger = logging.getLogger('Cook')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    while True:
        logger.info('Request Task')
        p = pickle.dumps({"method": REQ_ITEM})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Received %s', o)
    
        # get item from o and work in it. Implement each item.
   
        logger.info("Task Ready")
        p = pickle.dumps({"method": TASK_READY, "args": o})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
    
        if not o:
            break

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")

