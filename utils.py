from datetime import datetime
import logging

## TODO: use the python logging module
#https://docs.python.org/3/howto/logging.html#logging-basic-tutorial

class Utils:

    log_file = "log.txt"
    log_level = 3
    def log(message, error_level):
        log_code = {1:"Error", 2:"Warning", 3:"Info"}
        date = datetime.now().strftime("%y%m%d:%H%M%S")

        if(error_level > Utils.log_level): return
        print(f"{date} - {log_code[error_level]}: {message}")
