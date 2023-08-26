import asyncio
from functools import wraps

import click
from structlog import get_logger

from swap.indexer import run_indexer

import os
import sys

logger = get_logger(__name__)


indexer_id = "python-test-444"


def async_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@cli.command()
# @click.option("--server-url", default=None, help="server url.")
# @click.option("--mongo-url", default=None, help="MongoDB url.")
# @click.option("--rpc-url", default=None, help="StarkNet RPC url.")
@click.option("--restart", is_flag=True, help="Restart indexing from the beginning.")
@async_command
async def indexer(restart):
    server_url = os.environ.get('SERVER_URL', None)
    if server_url is None:
        sys.exit("SERVER_URL not set")
    mongo_url = os.environ.get('MONGO_URL', None)
    if mongo_url is None:
        sys.exit("MONGO_URL not set")
    rpc_url = os.environ.get('RPC_URL', None)
    if rpc_url is None:
        sys.exit("RPC_URL not set")
    apibara_auth_token = os.environ.get('APIBARA_AUTH_TOKEN', None)
    if apibara_auth_token is None:
        sys.exit("APIBARA_AUTH_TOKEN not set")
    logger.info(
        "starting indexer",
        server_url=server_url,
        # skip mongo_url: contains password
        rpc_url=rpc_url,
        restart=restart,
    )
    await run_indexer(server_url, apibara_auth_token, mongo_url, rpc_url, indexer_id, restart)
