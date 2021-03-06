#!/usr/bin/python3
import hashlib
import mmap
import multibase
import os
import re
import subprocess
import sys
import unixfs_pb2

try:
    isofile = sys.argv[1]
except Exception:
    print("usage: %s ISO" % sys.argv[0])
    exit(1)
isohashfile = isofile+".hashes"
if not os.path.isfile(isohashfile):
    file_path = os.path.realpath(__file__)
    subprocess.run([os.path.dirname(file_path)+"/prehash.py", isofile])
hashfd = open(isohashfile, "r")
hashdict = dict()
while True:
    line = hashfd.readline()
    if not line:
        break
    a = line.strip().split(" ")
    if not a[2] in hashdict:
        hashdict[a[2]] = list()
    if int(a[1]) <= 0:
        continue
    hashdict[a[2]].append([a[0], int(a[1]), a[3]])
hashfd.close()
if len(hashdict) < 70:
    print("too small hashdict - aborting - please check")
    exit(1)
isofd = open(isofile, "rb")
mm = mmap.mmap(isofd.fileno(), 0, prot=mmap.PROT_READ)
offs = 0

unixfsnode = unixfs_pb2.PBNode()
dataparsed = unixfs_pb2.Data()
dataparsed.Type = unixfs_pb2.Data.DataType.File
dataparsed.filesize = 0
aggregateddata = b""
filesn = 0
paddingn = 0
nonfileblockn = 0
paddinghashes = {}
with subprocess.Popen(["ipfs", "ls", "--size=false", "--resolve-type=false", "bafybeidobwhbiidzroyewbj6vzgudp7zen6x6cjm5xm4j3sp3zmvwzc5u4"], stdout=subprocess.PIPE) as proc:
    while(1):
        line = proc.stdout.readline()
        if not line:
            break
        m = re.search("^(\\S+) +([0-9]+)$", line.decode())
        cid = m.group(1)
        file = m.group(2)
        paddinghashes[int(file)] = cid

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def add_chunk(CID, size):
    link = unixfs_pb2.PBLink()
    link.Hash = multibase.decode(CID)
    link.Tsize = size
    unixfsnode.Links.extend([link])
    dataparsed.filesize += size
    dataparsed.blocksizes.extend([size])


def add_block(data):
    # store block
    with subprocess.Popen(["ipfs", "add", "--pin=false", "--cid-version", "1", "--raw-leaves", "--inline", "-Q"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        proc.stdin.write(data)
        proc.stdin.close()
        CID = proc.stdout.readline().decode()
    CID = CID[0:-1]
    debug("Adding CID="+CID)
    add_chunk(CID, len(data))
    return 0


def flush_aggregate():
    global aggregateddata
    if not aggregateddata:
        return
    add_block(aggregateddata)
    aggregateddata = b""


def add_block_aggregate(data):
    # check if we can/should aggregate
    if len(data) < 2048 and not re.search(b"[^\000]", data):
        flush_aggregate()
        CID = paddinghashes[len(data)]
        add_chunk(CID, len(data))
        return
    global aggregateddata
    aggregateddata = aggregateddata + data
    if len(aggregateddata) >= 256*1024:
        flush_aggregate()


while True:
    data = isofd.read(2048)
    if len(data) == 0:
        break
    found = False
    m = hashlib.sha256(data)
    shahash = m.hexdigest()
    if shahash in hashdict:
        f = hashdict[shahash]
        size = f[0][1]
        debug("found file at offs %i with %i candidates, size=%i" % (offs, len(f), size))  # debug
        fullmatches = list()
        for candidate in f:
            # find the longest match
            size = candidate[1]
            if size <= 2048:  # small files are already verified
                fullmatches.append(candidate)
            else:
                # for others we need to verify the full hash
                m = hashlib.sha256()
                m.update(mm[offs:offs+size])
                if m.hexdigest() == candidate[2]:
                    fullmatches.append(candidate)
        if len(fullmatches):
            largestmatch = fullmatches[0]
            for fullmatch in fullmatches[1:]:
                if fullmatch[1] > largestmatch[1]:
                    largestmatch = fullmatch
            size = largestmatch[1]
            debug("largest match", largestmatch)
            flush_aggregate()
            add_chunk(largestmatch[0], size)
            isofd.seek(offs+size, 0)
            # add padding chunk
            paddingbytes = (2048-size) % 2048
            if paddingbytes > 0:
                data = isofd.read(paddingbytes)
                debug("add padding chunk of %i bytes" % paddingbytes)
                add_block_aggregate(data)
                paddingn += 1
            offs += size+paddingbytes-2048
            found = True
            filesn += 1

    if not found:
        debug("no file found at offset %i" % offs)
        # add non-file data chunk (can merge chunks later)
        add_block_aggregate(data)
        nonfileblockn += 1
    offs += 2048


flush_aggregate()
debug("finalizing...")
unixfsnode.Data = dataparsed.SerializeToString()
nodebytes = unixfsnode.SerializeToString()
debug("Got dag-pb bytes=%i files=%i padding=%i nonfile=%i" % (len(nodebytes), filesn, paddingn, nonfileblockn))
if len(nodebytes) >= 1024*1024:
    print("The jigsaw DAG object is too large")
    exit(1)
with open(isofile+".dag-pb", "wb") as f:
    f.write(nodebytes)
    f.close()
putcmd = "ipfs --upgrade-cidv0-in-output dag put --pin --input-codec dag-pb --store-codec dag-pb".split(" ")
putcmd.append(isofile+".dag-pb")
subprocess.run(putcmd)
