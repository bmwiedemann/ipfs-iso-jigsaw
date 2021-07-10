#!/usr/bin/python3
import hashlib
import os
import re
import subprocess
import sys

try:
    isofile = sys.argv[1]
except Exception:
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
hashfile = open(isofile+".hashes", "w")
with subprocess.Popen(["ipfs", "add", "-H", "--pin=false", "--cid-version", "1", "--raw-leaves", "-r", "mnt/"], stdout=subprocess.PIPE) as proc:
    while(1):
        line = proc.stdout.readline()
        if not line:
            break
        m = re.search("^added (\\S+) (.*)$", line.decode())
        cid = m.group(1)
        file = m.group(2)
        if not os.path.isfile(file):
            continue
        size = os.path.getsize(file)
        hashfile.write("%s %i %s %s\n" % (cid, size, hash2048(file), hashall(file)))
hashfile.write(
    "bafkreifnp6wlewdpy3uwnqae27i5c2ycj5mal734wr6hvbo2xwfurcjmu4 4096 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7 zero4k\n\
bafkreie7dxf4gxbvbvqcp6ml4d24rnb3ilfffn3airm4brbl4ovirej5i4 8192 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad 9f1dcbc35c350d6027f98be0f5c8b43b42ca52b7604459c0c42be3aa88913d47 zero8k\n\
bafkreicp462zv5w6hntfwz3yrtbptgesvobh56xdurttikz3wtr3zds37y 16384 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad 4fe7b59af6de3b665b67788cc2f99892ab827efae3a467342b3bb4e3bc8e5bfe zero16k\n\
bafkreigdkaqeooxndndeftlsnswxe63d77zieswwrtw5p75xhr6l3ciepe 32768 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad c35020473aed1b4642cd726cad727b63fff2824ad68cedd7ffb73c7cbd890479 zero32k\n\
bafkreig6f4swazfav54xor6cxf2qlxalt467bxspjcpky4y4eoxjzkomge 65536 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31 zero64k\n\
bafkreih2imrzxtxhxf6kmlyaptdijb2wbi46dh3u6po6osdnwp4y36heoe 131072 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad fa43239bcee7b97ca62f007cc68487560a39e19f74f3dde7486db3f98df8e471\n\
bafkreiekhhjkxu4ztk3tyng3er3ijhg56mb44oe3gwbgquhzu4afrg2ksa 262144 e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad 8a39d2abd3999ab73c34db2476849cddf303ce389b35826850f9a700589b4a90\n\
")
umount()
