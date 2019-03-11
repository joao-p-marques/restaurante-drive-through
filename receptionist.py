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
    logger = logging.getLogger('Receptionist')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    mu=0.01, sigma=0.005

    while True:
        logger.info('Waiting for new order')
        p = pickle.dumps({"method": REQ_TASK})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Received %s', o)
        # receives request from client
    
        # generate the number of seconds the work will take
        seconds = math.fabs(random.gauss(mu, sigma))
        self.logger.info('Will work for %f seconds', seconds)
        # work(sleep) for the previous amount of seconds
        work(seconds)
   
        # processes order's items and puts them into each queue
        logger.info('Putting items in respective queue')
        for item in o[1].items():
            if item[0] == "hamburger":
                p = pickle.dumps({"method": PUT_HAMBURGER, "args": item[1]}) # pass argument and quantity as argument
            elif item[0] == "fries":
                p = pickle.dumps({"method": PUT_FRIES, "args": item[1]}) # pass argument and quantity as argument
            elif item[0] == "drink":
                p = pickle.dumps({"method": PUT_DRINK, "args": item[1]}) # pass argument and quantity as argument
            socket.send(p)

        # put order in pending queue
        logger.info("Putting order in pending queue")
        p = pickle.dumps({"method": PUT_IN_PENDING, "args": o})
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

