#!/usr/bin/perl -w
use Getopt::Long;
use strict;
use tracker;
use container;
use rfile;

BEGIN
{
    use File::Spec::Functions qw(rel2abs);
    use File::Basename;
    my $dirname=dirname(rel2abs($0));
    push @INC, $dirname;
}

use File::Spec::Functions qw(rel2abs);
use File::Basename;
my $dirname=dirname(rel2abs($0));
#die "$sample_count";
#my $t = new tracker(12);
#print $white->tostring(), "\n";
# process historical data
my $db_file = "$dirname/loto_hist.db";




my $file = new rfile($db_file);
my $w  = new container( 'white', 1, 59 );

sub get_oldest($$$)
{
    my ($data, $size, $drop) = @_;
    return () if (!defined($data));
    my @sorted = sort {$b->get_age() <=> $a->get_age()} @{$data};
    
    my @result;
    my $i = $size;
    foreach my $s (@sorted)
    {
	$drop --;
	next if ( $drop >= 0 );
	last if($i<=0);
	push @result, $s;
	$i--;
    }
    return @result;
}

my %last_numbers;
while( defined(my $entry = $file->next()))
{
    $w->age();
    my @whites = $entry->white();
    my $found = 1;
    foreach my $tw(@whites)
    {
	$w->set_age(int($tw), 0 );
    }
    my $r = "";
    foreach my $w(@whites)
    {
	if( !defined($last_numbers{$w}))
	{
	    $found = 0;
	    last;
	}
	$r .= " $w ";
    }
    if($found == 1)
    {
	print $entry->date(), "\n";
	print "[";
	foreach my $t (keys %last_numbers)
	{
	    print $last_numbers{$t}->get_number(), " ";
	}
	print "] ";
	print "***************** found $r\n";
    }
    my @trackers = $w->get_trackers();
    #9, 19, 29, 39, 49, 59
    my $start = 1;
    my @buckets = ( undef, undef, undef, undef, undef, undef );
    foreach my $t(@trackers)
    {
	my $n = $t->get_number();
	my $b = int($n/10);
	next if ($b == 1);
	my $tmp = $buckets[$b];
	if(!defined($tmp))
	{
	    my @tmp;
	    $buckets[$b] = \@tmp;
	    $tmp = $buckets[$b];
	}
	push @{$tmp}, $t;
	$buckets[$b] = $tmp;
	#print $t->tostring(), "\n";
    }
    my %last;
    foreach my $b (@buckets)
    {
	my @tmp = get_oldest($b, 5, 0);
	#print "[";
	foreach my $t (@tmp)
	{
	    #print $t->get_number(), " ";
	    $last{int($t->get_number())} = $t;
	}
	#print "] ";
    }
    %last_numbers = %last;
    #print "\n";
    
    #print $w->tostring(), "\n";
}
