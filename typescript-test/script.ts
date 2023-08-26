import type { Config } from "https://esm.sh/@apibara/indexer@0.1.2";
import type {
  Starknet,
} from "https://esm.sh/@apibara/indexer@0.1.2/starknet";
import type { Mongo  } from "https://esm.sh/@apibara/indexer@0.1.2/sink/mongo";


export const config: Config<Starknet, Mongo> = {
  streamUrl: "https://mainnet.starknet.a5a.ch",
  network: "starknet",
  filter: {
    header: {
      weak: false,
    },
    events: [
      {
        fromAddress:
          "0x01b22f7a9d18754c994ae0ee9adb4628d414232e3ebd748c386ac286f86c3066",
          //  keys: [hash.getSelectorFromName("Transfer")]
      },
    ],
  },
  finality: "DATA_STATUS_ACCEPTED",
  startingBlock: 54_900,
  sinkType: "mongo",
  sinkOptions: {
    database: "typescript-test-12345",
    collectionName: "blocks",
    connectionString: "mongodb://apibara:apibara@mongo:27017"
  },

};
let num = 0;
let blocksToProcced = 20001

// Transform each batch of data using the function defined in starknet.js.
export default function transform(batch) {
  console.time('test1');
  return batch.flatMap(decodeTransfersInBlock);
}

function decodeTransfersInBlock({ header, events }) {
  num += 1;
  if (num >= blocksToProcced){
    console.timeEnd('test1');
    throw new Error("Ended");
  }
  const { blockNumber, blockHash, parentBlockHash, timestamp } = header;
  // console.log(typeof(blockNumber));
  // console.log(`blockNumber: ${blockNumber}`);
  // console.log(`blockHash: ${blockHash}`);
  // console.log(`parent_block_hash: ${parentBlockHash}`);
  // console.log(`timestamp: ${timestamp}`);

  return {
    number: blockNumber,
    hash: blockHash,
    parent_hash: parentBlockHash,
    // hash: FieldElement.toHex(FieldElement.toBigInt(blockHash)),
    // parent_hash: FieldElement.toHex(FieldElement.toBigInt(parent_block_hash)),
    timestamp: new Date(timestamp),
  };
}
