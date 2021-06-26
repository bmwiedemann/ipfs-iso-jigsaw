#!/usr/bin/python3
import hashlib
import os
import re
import subprocess
import sys

try:
    isofile = sys.argv[1]
except:
    print("usage: %s ISO" % sys.argv[0])
    exit(1)

def umount():
    subprocess.run(["fusermount", "-u", "mnt"])

def hash2048(fname):
    data = ""
    with open(fname, "rb") as f:
        data = f.read(2048)
    while len(data) < 2048:
        data += b"\000"
    return hashlib.sha256(data).hexdigest()

def hashall(fname):
    sha = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

if os.path.isdir('mnt/media.1'):
    umount()

if not os.path.isdir('mnt'):
    os.mkdir("mnt")

subprocess.run(["fuseiso", isofile, "mnt"])
with subprocess.Popen(["ipfs", "add", "-H", "--pin=false", "--cid-version", "1", "--raw-leaves", "-r", "mnt/"], stdout=subprocess.PIPE) as proc:
    while(1):
        line = proc.stdout.readline()
        if not line:
            break
        m = re.search("^added (\S+) (.*)$", line.decode())
        cid = m.group(1)
        file = m.group(2)
        if not os.path.isfile(file):
            continue
        size = os.path.getsize(file)
        print(cid, size, hash2048(file), hashall(file))
