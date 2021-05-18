import logging
import bot_main

debug = True

# Configure root (global) logger
root_logger = logging.getLogger('')
root_logger.setLevel(logging.NOTSET)

# Configure logging handlers
std_out = logging.StreamHandler()
std_out.setLevel(logging.INFO)
log_file = logging.FileHandler('bot.log', mode='w', encoding="UTF-8")
log_file.setLevel(logging.INFO)
debug_log = logging.FileHandler('debug.log', mode='w', encoding="UTF-8")
debug_log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s  %(name)-8s : %(levelname)-7s : %(message)s", "%Y%m%d::%H:%M:%S")
debugformat = logging.Formatter("%(asctime)s  %(name)-8s : %(funcName)-10s : %(levelname)-7s : %(message)s", "%Y%m%d::%H:%M:%S")
std_out.setFormatter(format)
log_file.setFormatter(format)
debug_log.setFormatter(debugformat)

root_logger.addHandler(std_out)
root_logger.addHandler(log_file)
if (debug): root_logger.addHandler(debug_log)

# configure local logger
log = logging.getLogger(__name__)

log.info("Starting bot")
bot_main.run_bot()
