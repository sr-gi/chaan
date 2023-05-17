import os
import sys
import bz2
from tqdm import tqdm
from bitcoinrpc.authproxy import AuthServiceProxy

from lntopo.parser import ChannelAnnouncement
from lntopo.common import DatasetStream


def read_last_line(fin):
    try:
        fin.seek(-2, os.SEEK_END)
    except OSError:
        return
    while fin.read(1) != b"\n":
        fin.seek(-2, os.SEEK_CUR)
    return fin.readline().decode()


def get_last_line_number(fin_name):
    last_line = read_last_line(open(fin_name, "rb")) if os.path.isfile(fin_name) else None
    return int(last_line.split(":")[0]) if last_line else 0


def parse_dataset(fin, tmp_file):
    ann = set()
    dataset = DatasetStream(bz2.open(fin, "rb"))
    for m in tqdm(dataset, "Filtering gossip data"):
        if isinstance(m, ChannelAnnouncement):
            ann.add(m.short_channel_id)

    # Create an intermediary file so we can start from here if something breaks
    with open(tmp_file, "w") as f:
        for i, a in enumerate(ann, 1):
            f.write(f"{i}:{a}\n")

    return i


def main():
    if len(sys.argv) != 5:
        exit("Usage:\npoetry run chaan <rpcuser> <rpcpassword> <rpcconnect> <gossip_file>")

    fout_prefix = sys.argv[4].split("/")[-1].split(".")[0]
    tmp_file = f"chaan-{fout_prefix}-tmp.txt"
    out_file = f"chaan-{fout_prefix}.txt"

    # We first get all unique channel ids (add them to a set to make sure there are no duplicates)
    if os.path.isfile(tmp_file):
        if input(f"tmp file from a previous run found, would you like to skip the initial dataset parsing? (y/N)\n").lower() == "y":
            print("Skipping initial data parsing")
            fin_line_count = get_last_line_number(tmp_file)
        else:
            fin_line_count = parse_dataset(sys.argv[4], tmp_file)
    else:
        fin_line_count = parse_dataset(sys.argv[4], tmp_file)

    # This approach is obviously not bulletproof, given that the files may differ in any other place.
    # However, it should be good enough as long as we don't mess manually mess up with the files
    s = get_last_line_number(out_file)
    if s == fin_line_count:
        if input("A complete output file from a previous run was found. Do you like to run this again? (y/N)\n").lower() != "y":
            return
    elif s > 0 and input("An incomplete output file from a previous run was found. Do you like to resume? (y/N)\n").lower() != "y":
        return

    # Then we connect to our node and query the txid:index pair from the sci
    bitcoin_cli = AuthServiceProxy(f"http://{sys.argv[1]}:{sys.argv[2]}@{sys.argv[3]}:8332")
    with open(tmp_file, "r") as fin:
        with open(out_file, "w" if not s else "a") as fout:
            for ann in tqdm(fin.readlines()[s:], "Parsing data from bitcoind"):
                block_n, tx_n, i = ann.split(":")[1].split("x")
                block = bitcoin_cli.getblock(bitcoin_cli.getblockhash(int(block_n)))
                txid = block.get("tx")[int(tx_n)]
                fout.write(f"{ann.strip()}={txid}:{i}")
