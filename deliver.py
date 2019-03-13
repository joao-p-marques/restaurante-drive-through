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
    logger = logging.getLogger('Deliver')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    while True:
        # retrieve item from pending_queue 
        logger.info('Request Item from Pending Queue')
        p = pickle.dumps({"method": REQ_DELIVER_PENDING})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Received %s', o)
    
        # Retrieve item from request from ready_queue 
        for item in o[1].items():
            # retrieve item from ready_queue
            logger.info('Retrieve item from ready queue')
            if item[0] == 'hamburger':
                p = pickle.dumps({'method': GET_HAMBURGER, 'args': item[1]}) # send food type + quantity
            elif item[0] == "fries":
                p = pickle.dumps({"method": GET_FRIES, "args": item[1]}) # send food type + quantity
            elif item[0] == "drink":
                p = pickle.dumps({"method": GET_DRINK, "args": item[1]}) # send food type + quantity
            socket.send(p)
   
        # Put item in delivery_queue 
        logger.info('Putting item into delivery queue')
        p = pickle.dumps({'method': PUT_IN_DELIVERY})
        pickle.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
    
        if not o:
            break

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")
