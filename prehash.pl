#!/usr/bin/perl -w
use strict;
use Digest::SHA1  qw(sha1_hex);

my $file=shift;
die "usage: $0 ISO\n" unless $file;

sub umount() { system(qw"fusermount -u mnt"); } #TODO: ignore stderr

sub hash2048($)
{ my $file = shift;
  open(my $fd, "<", $file) or die "error opening $file: $!";
  my $data;
  read($fd, $data, 2048);
  close($fd);
  return sha1_hex($data);
}

if(-d "mnt/media.1") {umount()}
mkdir("mnt");
system("fuseiso", $file, "mnt")==0 or die "error in fuseiso: $!";
#system("ls", "mnt");

open(PIPE, "-|", "ipfs add -H --pin=false --cid-version 1 --raw-leaves -r mnt/") or die "ipfs add failed: $!";
while(<PIPE>) {
  print $_;
  m/^added (\S+) (.*)$/ or die;
  my $cid = $1;
  my $file = $2;
  my $hash2048 = hash2048($file);
}
umount();
