import logging

class ServerLogger:
    """
    A utility class that configures and then can provide a logger instance for server-side logging.

    Args:
        name (str): The name of the logger, typically the name of the log file.

    Attributes:
        logger (logging.Logger): The configured logger instance.

    Methods:
        __init__(self, name):
        get(self):

    Example:
        >>> ServerLogger("server.log").get()
    """

    def __init__(self, name):
        """
        Initialize a ServerLogger with the given name.

        Args:
            name (str): The name of the logger, typically the name of the log file.

        Notes:
            Sets the loggger's log level to DEBUG, configures the log message format, and setups logs to ouput to a file and the console.
        """
        name = name.replace('.log','')
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                          datefmt='%m/%d/%Y %I:%M:%S %p')  
        fh = logging.FileHandler(name + ".log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger

    def get(self):
        """
        Get the configured logger instance.

        Returns:
            logging.Logger: The configured logger instance for server-side logging.

        Example:
            >>> ServerLogger("server.log").get()
        """
        return self.logger