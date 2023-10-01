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
        >>> ServerLogger("tuneease.log").get()
    """

    logged_messages = set()

    def __init__(self, name="tuneease.log"):
        """
        Initialize a ServerLogger with the given name.

        Args:
            name (str): The name of the logger, typically the name of the log file.

        Notes:
            Sets the loggger's log level to DEBUG, configures the log message format, and setups logs to ouput to a file and the console.
        """
        self.name = name.replace(".log", "")
        self.logger = logging.getLogger(name)

    def get(self):
        """
        Get the configured logger instance.

        Returns:
            logging.Logger: The configured logger instance for server-side logging.

        Example:
            >>> ServerLogger("tuneease.log").get()
        """
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )
        filehandler = logging.FileHandler(self.name + ".log")
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)
        streamhandler = logging.StreamHandler()
        streamhandler.setLevel(logging.INFO)
        streamhandler.setFormatter(formatter)
        streamhandler.addFilter(self.filter)
        self.logger.addHandler(streamhandler)
        return self.logger

    def filter(self, record):
        msg = record.getMessage()
        if msg in self.logged_messages:
            return False
        self.logged_messages.add(msg)
        return True
