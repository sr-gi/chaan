import os
import sys
import bz2
from tqdm import tqdm
from bitcoinrpc.authproxy import AuthServiceProxy

from lntopo.parser import ChannelAnnouncement
from lntopo.common import DatasetStream


def main():
    argv_len = len(sys.argv)
    if argv_len < 5:
        exit("Usage:\npoetry run chaan <rpcuser> <rpcpassword> <rpcconnect> <gossip_file> [<skip_filtering> <start_line>]")

    fout_prefix = sys.argv[4].split("/")[-1].split(".")[0]
    tmp_file = f"chaan-{fout_prefix}-tmp.txt"
    out_file = f"chaan-{fout_prefix}.txt"

    if argv_len < 6 or (argv_len > 5 and not sys.argv[5].lower() in ['true', '1']):
        # We first get all unique channel ids (add them to a set to make sure there are no duplicates)
        c_ann = set()
        dataset = DatasetStream(bz2.open(sys.argv[4]))
        for m in tqdm(dataset, "Filtering gossip data"):
            if isinstance(m, ChannelAnnouncement):
                c_ann.add(m.short_channel_id)

        # Create an intermediary file so we can start from here if something breaks
        with open(tmp_file, "w") as f:
            for a in c_ann:
                f.write(f"{a}\n")
    elif not os.path.isfile(tmp_file):
        exit(f"Cannot skip gossip parsing, {tmp_file} not found")
    else:
        print("Skipping gossip data filtering")

    # Then we connect to our node and query the txid:index pair from the sci
    bitcoin_cli = AuthServiceProxy(f"http://{sys.argv[1]}:{sys.argv[2]}@{sys.argv[3]}:8332")

    with open(tmp_file, "r") as fin:
        with open(out_file, 'a') as fout:
            s = int(sys.argv[6]) if argv_len > 6 else 0
            if s > 0:
                print(f"Skipping the first {s} lines")
            for ann in tqdm(fin.readlines()[s:], "Parsing data from bitcoind"):
                block_n, tx_n, i = ann.split("x")
                block = bitcoin_cli.getblock(bitcoin_cli.getblockhash(int(block_n)))
                txid = block.get("tx")[int(tx_n)]
                fout.write(f"{ann.strip()}={txid}:{i}")
