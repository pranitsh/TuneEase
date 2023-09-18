import logging

class ServerLogger:
    def __init__(self, name):
        name = name.replace('.log','')
        logger = logging.getLogger(name)    # Define the logger with the specified name
        logger.setLevel(logging.DEBUG)      # Set the logger level to DEBUG

        # Define the format of the log messages including time, name of logger, level of log and message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                          datefmt='%m/%d/%Y %I:%M:%S %p')  

        # Create a file handler and set its level to DEBUG
        fh = logging.FileHandler(name + ".log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)        

        # Create a console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger

    def get(self):
        # Get the instance of logger
        return self.logger