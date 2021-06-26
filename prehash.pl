#!/usr/bin/perl -w
# pre-hash files in an ISO
use strict;
use Digest::SHA1  qw(sha1_hex);

my $isofile=shift;
die "usage: $0 ISO\n" unless $isofile;

sub umount() { system(qw"fusermount -u mnt"); } #TODO: ignore stderr

sub hash2048($)
{ my $file = shift;
  open(my $fd, "<", $file) or die "error opening $file: $!";
  binmode $fd;
  my $data;
  read($fd, $data, 2048);
  close($fd);
  $data .= "\000" x (2048-length($data)); # pad to ISO sector size
  return sha1_hex($data);
}
sub hashall($)
{ my $file = shift;
  my $sha1 = Digest::SHA1->new;
  open(my $fd, "<", $file) or die "error opening $file: $!";
  binmode $fd;
  $sha1->addfile($fd);
  close($fd);
  return $sha1->hexdigest;
}

if(-d "mnt/media.1") {umount()}
mkdir("mnt");
system("fuseiso", $isofile, "mnt")==0 or die "error in fuseiso: $!";

open(PIPE, "-|", "ipfs add -H --pin=false --cid-version 1 --raw-leaves -r mnt/") or die "ipfs add failed: $!";
open(my $outfd, ">", "$isofile.hashes") or die $!;
while(<PIPE>) {
  print $_;
  m/^added (\S+) (.*)$/ or die;
  my $cid = $1;
  my $file = $2;
  next unless -f $file; # skip dirs and symlinks
  my $size = -s $file;
  my $hash2048 = hash2048($file);
  my $hashall = hashall($file);
  print $outfd "$cid $size $hash2048 $hashall\n";
}
umount();
