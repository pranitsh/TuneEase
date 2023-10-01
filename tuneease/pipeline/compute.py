import os


class Node:
    NODE_RANK = None
    MASTER_ADDR = None
    MASTER_PORT = None
    DIST_URL = None
    NUM_NODE = None

    def __init__(self) -> None:
        self.NODE_RANK = int(os.environ["INDEX"] if "INDEX" in os.environ else 0)

        self.MASTER_ADDR, self.MASTER_PORT = (
            (os.environ["CHIEF_IP"], 22275)
            if "CHIEF_IP" in os.environ
            else ("127.0.0.1", 29500)
        )
        self.DIST_URL = f"tcp://{self.MASTER_ADDR}:%{self.MASTER_PORT}"

        self.NUM_NODE = os.environ["HOST_NUM"] if "HOST_NUM" in os.environ else 1
