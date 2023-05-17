Usage:

```
poetry run chaan <rpcuser> <rpcpassword> <rpcconnect> <gossip_file> [<skip_filtering> <start_line>]
```

where:

- `rpc{user, password, connect}` match your `bitcoind` connection parameters
- `gossip_file` matches one of the datasets [provided by lntopo](https://github.com/lnresearch/topology#available-datasets)
- `skip_filtering` (optional) refers to whether the parsing of the `gossip_file` must be skipped. This is only possible if the parsing was already performed before
- `start_line` (optional) refers to the starting line in the parsing tmp file (created after parsing the `gossip_file`) from where the second half of the data parsing will start from


## What is `start_line` purpose?
`start_line` is useful in case the second half of the parsing (involving querying `bitcoind`) crashes for some reason, like the request timing out due to high load on your node. In that case, you can re-start the parsing where it was left by the last (unfinished) run.

To do so, we can just check what was the last line written by the `chaan`:

```
cat chann-XXX.txt | wc -l
```

And its content:

```
tail -1 chann-XXX.txt
> N1
```

Now we can compare the line number of that `scid` in the temporary file, both lines must match (`N1 == N2`)

```
cat chaan-XXX-tmp.txt | grep scid
> N2:scid
```

If so, `N1` is out `start_line`
