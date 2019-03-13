# coding: utf-8
import uuid
import logging
import threading
import pickle
from queue import Queue
import zmq
from utils import ORDER, REQ_TASK, TASK_READY, PICKUP, work

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


class Worker(threading.Thread):
    def __init__(self, context, i, backend, restaurant):
        # call the constructor form the parent class
        threading.Thread.__init__(self)

        self.socket = context.socket(zmq.REP)
        self.backend = backend
        self.restaurant = restaurant

        # store the necessary inputs
        self.logger = logging.getLogger('Worker '+str(i))

    def run(self):
        self.socket.connect(self.backend)

        self.logger.info('Start working')
        while True:
            p = self.socket.recv()
            o = pickle.loads(p)

            if o["method"] == ORDER:
                order_id = self.restaurant.add_order(o["args"])

                p = pickle.dumps(order_id)

            elif o["method"] == REQ_TASK:
                task = self.restaurant.get_task()

                p = pickle.dumps(task)

            elif o["method"] == TASK_READY:
                self.restaurant.ready(o["args"])

                p = pickle.dumps(True)

            elif o["method"] == PICKUP:
                order = self.restaurant.pickup(o["args"])
                
                p = pickle.dumps(order)

            self.socket.send(p)
        self.socket.close()


class DriveThrough():
    def __init__(self):
        self.orders = Queue()
        self.task = Queue()

    def add_order(self, order):
        order_id = uuid.uuid1()
        self.orders.put((order_id, order))
        return order_id

    def ready(self, order):
        self.task.put(order)

    def pickup(self, order_id):
        #TODO check order_id in the queue head
        return self.task.get()

    def get_task(self):
        return self.orders.get()

def main(ip, port):
    logger = logging.getLogger('Drive-through')

    logger.info('Setup ZMQ')
    context = zmq.Context()
    restaurant = DriveThrough()

    # frontend for clients (socket type Router)
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://{}:{}".format(ip, port))

    # backend for workers (socket type Dealer)
    backend = context.socket(zmq.DEALER)
    backend.bind("inproc://backend")

    # Setup workers
    workers = []
    for i in range(4):
        # each worker is a different thread
        worker = Worker(context, i, "inproc://backend", restaurant)
        worker.start()
        workers.append(worker)

    # Setup proxy
    # This device (already implemented in ZMQ) connects the backend with the frontend
    zmq.proxy(frontend, backend)

    # join all the workers
    for w in workers:
        w.join()

    # close all the connections
    frontend.close()
    backend.close()
    context.term()


if __name__ == '__main__':
main("127.0.0.1", "5001")
