#!/usr/bin/python3
import hashlib
import mmap
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
    hashdict[a[2]].append([a[0], int(a[1]), a[3]])
hashfd.close()
isofd = open(isofile, "rb")
mm = mmap.mmap(isofd.fileno(), 0, prot=mmap.PROT_READ)
offs = 0
while True:
    data = isofd.read(2048)
    if len(data) == 0:
        break
    m = hashlib.sha1(data)
    shahash = m.hexdigest()
    if shahash in hashdict:
        f = hashdict[shahash]
        size = f[0][1]
        print("found file at offs %i with %i candidates, size=%i" % (offs, len(f), size)) # debug
        fullmatches = list()
        for candidate in f:
            # find the longest match
            #print(candidate) # debug
            size = candidate[1]
            if size <= 2048: # small files are already verified
                fullmatches.append(candidate)
            else:
                # for others we need to verify the full hash
                m.update(mm[offs+2048:offs+size])
                if m.hexdigest() == candidate[2]:
                    fullmatches.append(candidate)
            if len(fullmatches):
                largestmatch = fullmatches[0]
                for fullmatch in fullmatches[1:]:
                    if fullmatch[1] > largestmatch[1]:
                        largestmatch = fullmatch
                print(largestmatch)

    offs += 2048

