#!/bin/env perl

use strict;
use NetAddr::IP;
use Data::Dumper;

sub usage() {
  print "Usage: $0 [-d] [network [count]]\n";
  print "Generate \$count (default 1) addresses from \$network (default any)\n";
  exit 0;
}

my $debug = 0;
if($ARGV[0] eq '-d') { $debug=1; shift @ARGV; }
if($ARGV[0] eq '-h') { usage(); }

my $ip = NetAddr::IP->new(defined($ARGV[0])?$ARGV[0]:'any');
if($ip->bits() != 32) {
  warn("Sorry, IPv4 only right now.\n");
  exit 2;
}

my $net = $ip->network();
my $size = $ip->num();

if($ip->masklen()<31) { $size += 2; } ### Include network address and broadcast
if($ip->masklen() == 0) { $size = 224 * 2**24; }

my %generated;

my $count=defined($ARGV[1])?$ARGV[1]:1;
if ($count>$size) {
  warn("Count ($count) greater than network size ($size). I will generate $size addresses only.\n");
  $count=$size;
}

warn "S: $size\n" if $debug;

for(my $i=0; $i<$count; $i++) {
  my $rand_n = int(rand($size));
  redo if defined($generated{$rand_n});
  $generated{$rand_n}=1;
  warn "r: $rand_n\n" if $debug;
}

my $t = NetAddr::IP->new();
if($ip->masklen() == 0) {
  my $net2 = NetAddr::IP->new('128/1');
  map { if($_ >= 2**31) { $t=$net2+($_-2**31); } else { $t=$net+$_ }; print $t->addr()."\n" } keys %generated;
}else {
  map { $t=$net+$_; print $t->addr()."\n" } keys %generated;
}
