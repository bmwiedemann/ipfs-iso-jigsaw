#!/usr/bin/python3
import hashlib
import sys

try:
    isofile = sys.argv[1]
except:
    print("usage: %s ISO" % sys.argv[0])
    exit(1)
hashfd = open(isofile+".hashes", "r")
hashdict = dict();
while True:
    line = hashfd.readline()
    if not line:
        break
    a = line.strip().split(" ")
    if not a[2] in hashdict:
        hashdict[a[2]] = list()
    hashdict[a[2]].append([a[0], int(a[1])])
hashfd.close()
isofd = open(isofile, "rb")
offs = 0
while True:
    data = isofd.read(2048)
    if len(data) == 0:
        break
    shahash = hashlib.sha1(data).hexdigest()
    if shahash in hashdict:
        f = hashdict[shahash]
        size = f[0][1]
        print("found file at offs %i with %i candidates, size=%i" % (offs, len(f), size))
    offs += 2048

