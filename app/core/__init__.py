from os import urandom
from models.db import eth_cli

secret_key = urandom(512)
blockFilter = eth_cli.eth_newBlockFilter()
