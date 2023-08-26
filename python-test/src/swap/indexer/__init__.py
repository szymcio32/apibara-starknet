from decimal import Decimal

import logging
import asyncio
import time

from apibara.indexer import IndexerRunner, IndexerRunnerConfiguration, Info
from apibara.indexer.indexer import IndexerConfiguration, Reconnect
from apibara.protocol.proto.stream_pb2 import Cursor, DataFinality
from apibara.starknet import EventFilter, Filter, StarkNetIndexer, felt
from apibara.starknet.cursor import starknet_cursor
from apibara.starknet.proto.starknet_pb2 import Block, BlockHeader
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from structlog import get_logger

from swap.indexer.context import IndexerContext

FACTORY_ADDRESS = felt.from_hex("0x01b22f7a9d18754c994ae0ee9adb4628d414232e3ebd748c386ac286f86c3066")
# FACTORY_ADDRESS = felt.from_hex("0x00dad44c139a476c7a17fc8141e6db680e9abc9f56fe249a105094c44382c2fd")
# PAIR_CREATED_KEY = felt.from_hex("0x19437bf1c5c394fc8509a2e38c9c72c152df0bac8be777d4fc8f959ac817189")
index_from_block = 54_900
logger = get_logger(__name__)

# Print apibara logs
root_logger = logging.getLogger("apibara")
# change to `logging.DEBUG` to print more information
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(logging.StreamHandler())
num = 0
start = time.time()

class JediSwapIndexer(StarkNetIndexer):
    _indexer_id: str

    def __init__(self, indexer_id):
        self._indexer_id = indexer_id
        super().__init__()

    def indexer_id(self) -> str:
        return self._indexer_id
    
    def initial_configuration(self) -> Filter:
        # Return initial configuration of the indexer.
        return IndexerConfiguration(
            filter=Filter()
            .with_header(weak=False)
            .add_event(
                EventFilter()
                .with_from_address(FACTORY_ADDRESS)
                # .with_keys([PAIR_CREATED_KEY])
            ),
            starting_cursor=starknet_cursor(index_from_block),
            finality=DataFinality.DATA_STATUS_ACCEPTED,
        )

    async def handle_data(self, info: Info, data: Block):
        await handle_block(info, data.header)
        # await handle_events(self, info, data)
    
    async def handle_reconnect(self, exc: Exception, retry_count: int) -> Reconnect:
        await asyncio.sleep(10 * retry_count)
        return Reconnect(reconnect=retry_count < 5)

async def handle_block(info: Info, block_header: BlockHeader):
    # Store the block information in the database.
    global num
    num += 1
    if num >= 20001:
        end = time.time()
        result = end - start
        logger.info(result)
        raise Exception(f'end time: {result}')
    block = {
        "number": block_header.block_number,
        "hash": hex(felt.to_int(block_header.block_hash)),
        # "hash": block_header.block_hash,
        "parent_hash": hex(felt.to_int(block_header.parent_block_hash)),
        "timestamp": block_header.timestamp.ToDatetime(),
    }
    # logger.info(
    #     "handle block", block = block
    # )
    await info.storage.insert_one("blocks", block)


async def handle_events(indexer: JediSwapIndexer, info: Info, block: Block):
    pass


async def run_indexer(server_url, apibara_auth_token, mongodb_url, rpc_url, indexer_id, restart):
    runner = IndexerRunner(
        config=IndexerRunnerConfiguration(
            stream_url=server_url,
            storage_url=mongodb_url,
            token=apibara_auth_token,
        ),
        reset_state=restart,
        timeout=300,
    )

    context = IndexerContext(
        rpc=FullNodeClient(rpc_url, net=StarknetChainId.MAINNET),
        block_hash=0,
        block_number=0,
        block_timestamp=None,
        eth_price=Decimal("0"),
    )

    while True:
        await runner.run(JediSwapIndexer(indexer_id), ctx=context)
        logger.warn("disconnected. reconnecting.")

