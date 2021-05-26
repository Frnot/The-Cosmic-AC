import queue
import logging
from logging.handlers import QueueHandler, QueueListener
import bot_main

debug = True


# Configure logging handlers
format = logging.Formatter("%(asctime)s  %(name)-8s : %(levelname)-7s : %(message)s", "%Y%m%d::%H:%M:%S")
debugformat = logging.Formatter("%(asctime)s  %(name)-8s : %(funcName)-10s : %(levelname)-7s : %(message)s", "%Y%m%d::%H:%M:%S")

std_out = logging.StreamHandler()
std_out.setLevel(logging.INFO)
std_out.setFormatter(format)

log_file = logging.FileHandler('bot.log', mode='w', encoding="UTF-8")
log_file.setLevel(logging.INFO)
log_file.setFormatter(format)

debug_log = logging.FileHandler('debug.log', mode='w', encoding="UTF-8")
debug_log.setLevel(logging.DEBUG)
debug_log.setFormatter(debugformat)


# QueueHandler is coupled to QueueListener by the queue object
log_queue = queue.Queue(-1)

# Configure root (global) logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.NOTSET)
queue_handler = QueueHandler(log_queue)
root_logger.addHandler(queue_handler)

# Configure queue listener (add handlers to root logger) : QueueHandler ==log_queue==> QueueListener
if debug:
    listener = QueueListener(log_queue, std_out, log_file, debug_log, respect_handler_level=True)
else:
    listener = QueueListener(log_queue, std_out, log_file, respect_handler_level=True)

listener.start()



# configure local logger
log = logging.getLogger(__name__)

log.info("Starting bot")
bot_main.run_bot()

# Stop queue listener
listener.stop()
