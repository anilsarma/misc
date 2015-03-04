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

sub get_oldest($$$$)
{
    my ($data, $size, $drop, $skip) = @_;
    return () if (!defined($data));
    my @sorted = sort {$b->get_age() <=> $a->get_age()} @{$data};
     
    
    my @result;
    my $i = $size;
    my $sp = $skip;
    foreach my $s (@sorted)
    {
	$drop --;
	next if ( $drop >= 0 );
	if( $sp >0 )
	{
	    $sp--;
	    next;
	}
	$sp = $skip;
	
	last if($i<=0);
	push @result, $s;
	$i--;
    }
    return @result;
}

my %last_numbers;
my $age = 0;
my $tage = $age;
my $total_samples = 0;
my $total_wins = 0;
#foreach my $t (@trackers)
#    {
#	    print $t->tostring() , "\n";
#    }
my $prev_trackers = undef;
my @pos;
while( defined(my $entry = $file->next()))
{
    $w->age();
    $total_samples ++;
    my @whites = $entry->white();
    my $found = 1;
    my %whites ;
    foreach my $tw(@whites)
    {
	$w->set_age(int($tw), 0 );
	$whites{$tw} = $tw;
	#print "WH $tw\n";
    }
    my @trackers = $w->get_age_trackers();
    my @set;
    if( defined($prev_trackers))
    {
    for(my $i=0; $i < scalar(@{$prev_trackers});$i++)
    {
	 my $n = $prev_trackers->[$i]->get_number();    
	 if( defined($whites{$n}))
	 {
		 push @set, $i;
		 #print "$i=$n ";
	 }
    } 
    }
    $prev_trackers = \@trackers;
    #print "\n";
    foreach my $n(@set)
    {
	     print "$n ";
    }
     print "\n";
     push @pos, \@set;
}
