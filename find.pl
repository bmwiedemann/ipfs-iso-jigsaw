#!/usr/bin/perl -w
use strict;

my $iso = shift || "openSUSE-Tumbleweed-NET-x86_64-Snapshot20210307-Media.iso";
my $fd;
open($fd, "<", $iso) or die "cannot open iso $iso: $!";
my $size = -s $iso;
for(my $p=0 ; $p<$size ; $p+=2048) {
    my $data;
    #print "testing position $p\n";
    sysseek($fd, $p, 0);
    sysread($fd, $data, 30);
    if($data =~ m/\A\xed\xab\xee\xdb\x03/) {
    #ed ab ee db 03 00 00 01  00 01
        print "found rpm at offs $p\n";
        my $size = `rpm -qp --qf "%{LONGSIGSIZE}"`;
        $size += 4504;
    }
}
