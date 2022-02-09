#!/usr/bin/python3
import subprocess

subprocess.run(["ipfs", "files", "rm", "-r", "/padding"])
subprocess.run(["ipfs", "files", "mkdir", "/padding"])
for n in range(1,2048):
    data = b'\000' * n
    with subprocess.Popen(["ipfs", "add", "--pin=false", "--cid-version", "1", "--raw-leaves", "--inline", "-Q"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        proc.stdin.write(data)
        proc.stdin.close()
        CID = proc.stdout.readline().decode()
        subprocess.run(["ipfs", "files", "--flush=false", "cp", "/ipfs/" + CID, "/padding/"+str(n)])

subprocess.run(["ipfs", "files", "--upgrade-cidv0-in-output", "stat", "/padding"])
# => /ipfs/bafybeidobwhbiidzroyewbj6vzgudp7zen6x6cjm5xm4j3sp3zmvwzc5u4
