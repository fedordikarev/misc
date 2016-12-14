#!/usr/bin/perl

use Getopt::Std;
use strict;

my %opts;

my %listen_ports;
my %connected_ports;

my $pid=undef;
my $command;

my $list;
my $fh;

getopts("ilvpF:", \%opts);

if(defined($opts{F})) {
  open $fh, '<', $opts{F} or die("Cant open $opts{F}.");
}else {
  $list=`lsof -iTCP -n -P -Fcpn`;
  open $fh, '<', \$list;
}

my $ignore_loopback = not defined($opts{l});
my $verbose = defined($opts{v});
my $inverted = defined($opts{i});

my @filters = @ARGV;

while(<$fh>) {
  chomp;
  if($_ =~ /^p(\d+)$/) { $pid = $1; next; }
  if($_ =~ /^c(.+)$/) { $command = $1; next; }

  if($_ =~ /^n([\d\.]+):(\d+)\->([\d\.]+):(\d+)/) {
    next if($ignore_loopback and ($1 == "127.0.0.1"));
    $connected_ports{$2}->{pid} = $pid;
    $connected_ports{$2}->{local} = $1;
    $connected_ports{$2}->{remote} = $3;
    $connected_ports{$2}->{port} = $4;
    $connected_ports{$2}->{cmd} = $command;
    next;
  }
  if($_ =~ /^n\[([0-9a-f:]+)\]:(\d+)\->\[([0-9a-f:]+)\]:(\d+)/) {
    next if($ignore_loopback and ($1 == "::1"));
    $connected_ports{$2}->{pid} = $pid;
    $connected_ports{$2}->{local} = $1;
    $connected_ports{$2}->{remote} = $3;
    $connected_ports{$2}->{port} = $4;
    $connected_ports{$2}->{cmd} = $command;
    next;
  }
  if($_ =~ /^n([\d\.\*]+):(\d+)$/) {
    $listen_ports{$2} = $pid; next;
  }
  if($_ =~ /^n\[([0-9a-f:]+)\]:(\d+)$/) {
    $listen_ports{$2} = $pid; next;
  }
  if($_ =~ /^n/) { warn("> $_"); }
};

close $fh;

print "Listen ports: ".join(",", keys(%listen_ports))."\n" if($verbose);
print "Connected ports: ".join(",", keys(%connected_ports))."\n" if($verbose);

my @outbound = grep { ! exists($listen_ports{$_}) } keys(%connected_ports);

print "Outbound: ".join(",", @outbound)."\n" if($verbose);
my $count = 0;
foreach my $port (@outbound) {
  my $peer = $connected_ports{$port};
  my $match = (@filters>0)?0:not $inverted;
  foreach my $item (@filters) {
    my ($f_addr, $f_port) = split /:/, $item;
    my $match_addr=0;
    my $match_port=0;
    if(($f_addr eq '')or($f_addr eq '*')) {
      $match_addr = 1;
    }elsif($f_addr =~ qr(/)) { 
      eval "use NetAddr::IP; 1" or die("Need NetAddr::IP for network matching");
      my $ip = NetAddr::IP->new($f_addr);
      $match_addr = $ip->contains(NetAddr::IP->new($peer->{remote}));
    }else {
      $match_addr = ($f_addr eq $peer->{remote});
    }
    next unless($match_addr);
    if(($f_port eq '')or($f_port eq '*')) {
      $match_port = 1;
    }elsif($f_port =~ /^(\d+)\-(\d+)$/) {
      $match_port = (($peer->{port} >= $1) and ($peer->{port} <= $2));
    }else {
      $match_port = ($f_port == $peer->{port});
    }
    if($match_addr and $match_port) { $match = 1; last; }
  }
  if($match xor $inverted) {
    print "$peer->{cmd} [$peer->{pid}]\t" if(defined($opts{p}));
    print "$peer->{local}:$port -> $peer->{remote}:$peer->{port}\n";
    $count++;
  }
  # print `lsof -iTCP:$port -n -P -Fcpn`
};

exit ($count > 0)?1:0;
