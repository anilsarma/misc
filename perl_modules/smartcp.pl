#!/usr/bin/perl -I . -w
use strict;

use sync;
use strict;
use Getopt::Long;

(my $program_name=$0)=~ s|.+?/||;
my $verbose = 0;
my $sync_all = 1;
my $VERSION ="1.0";
sub usage()
{
    print STDERR "usage: $program_name <options> <source> <destination>\n";
    print STDERR "\tversion: $VERSION (c)???\n";
    sync::close();
    exit(0);
}

if( $#ARGV != 1)
{
    usage();
}
sync::fast_sync $ARGV[0], $ARGV[1];
sync::close();
