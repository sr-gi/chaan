### Usage:

```
poetry run chaan <rpcuser> <rpcpassword> <rpcconnect> <gossip_file>
```

where:

- `rpc{user, password, connect}` match your `bitcoind` connection parameters
- `gossip_file` matches one of the datasets [provided by lntopo](https://github.com/lnresearch/topology#available-datasets)


### Output format:

The generated output file (`chaan-gossip-DATE.txt`) has the following format:

```
n:scid=txid:out
```

Where:

- `n` is the line number within the file
- `scid` is the short channel id identifying this channel announcement
- `txid` is the transaction id of the funding transaction
- `out` is the index of the funding output


## Installation

This currently requires lntopo to be manually installed from the [repo](https://github.com/lnresearch/topology) given a [patch regarding net addresses](https://github.com/lnresearch/topology/commit/391e3ea8df7d17682e281c08d31c6e3980b228fd) is missing from PyPi. 