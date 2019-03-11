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
    logger = logging.getLogger('Client')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    while True:
        logger.info('Request some food')
        p = pickle.dumps({"method": ORDER, "args": {"hamburger": 1}})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Received %s', o)
        #receives object with ID of order and waits for it
    
        work(3)
   
        logger.info('Pickup order %s', o)
        p = pickle.dumps({"method": PICKUP, "args": o})
        socket.send(p)
         
        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Got %s', o)

        if not o:
            break

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")

