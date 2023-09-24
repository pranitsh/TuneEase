import os

NODE_RANK = int(os.environ['INDEX'] if 'INDEX' in os.environ else 0)

MASTER_ADDR, MASTER_PORT = (os.environ['CHIEF_IP'], 22275) if 'CHIEF_IP' in os.environ else ("127.0.0.1", 29500)
DIST_URL = f'tcp://{MASTER_ADDR}:%{MASTER_PORT}'

NUM_NODE = os.environ['HOST_NUM'] if 'HOST_NUM' in os.environ else 1