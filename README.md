We want to efficiently store iso images,
that change daily
but mostly contain the same files again
and we do want to re-use file CIDs
so we scan the .iso for these files
and chunk accordingly

This is tested on Linux

## Installation

see [INSTALL.md](INSTALL.md)

## Example usage

```bash
wget http://download.opensuse.org/distribution/leap/15.2/iso/openSUSE-Leap-15.2-NET-x86_64.iso
./prehash.py openSUSE-Leap-15.2-NET-x86_64.iso
./ipfsjigsaw.py openSUSE-Leap-15.2-NET-x86_64.iso
ipfs ls QmfKjz8VTPsBejKTkfLFWdRtjkFQvyFdFVrHi3vp4zVaLQ
```
