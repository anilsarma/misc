#!/usr/bin/perl -w
use Getopt::Long;
use strict;
use tracker;
use container;
BEGIN
{
    use File::Spec::Functions qw(rel2abs);
    use File::Basename;
    my $dirname=dirname(rel2abs($0));
    push @INC, $dirname;
}
# http://38.121.105.10/powerball/winnums-text.txt
# http://www.powerball.com/powerball/winnums-text.txt
#
#
# struct {
#   number  
#   frequency
#   age
#}
(my $program_name=$0)=~ s|.+?/||;
my $sort_order = "";


package main;
my $DEFAULT_SAMPLE_COUNT=100000; #120; # 2 years
my $sample_count = $DEFAULT_SAMPLE_COUNT;
my $end_date = undef;
my $download = 0;
sub usage($)
{
    my ($msg) = @_;
    print STDERR "error: $msg\n" if (defined($msg));
    print STDERR "usage: $program_name <options> \n";
    print STDERR "\tversion:\n";
    print STDERR "options:\n";
    print STDERR "       -samples <sample count>  total number of samples to use default $DEFAULT_SAMPLE_COUNT\n";
    print STDERR "       -end  <date>             all samples before this date\n";
    print STDERR "       -download  the latest database\n";
    print STDERR "       -sort <option>   values are 'freq' default is 'age' \n";

    exit(0);
}
GetOptions(  "help"           =>   sub { usage(undef); },
	     "samples=s"      => \$sample_count,
	     "end_date=s"     => \$end_date,
	     "download"       => sub { $download = 1; },
	     "sort=s"         => \$sort_order
    )|| usage("invalid arguments");

use strict;
use File::Spec::Functions qw(rel2abs);
use File::Basename;
my $dirname=dirname(rel2abs($0));
#die "$sample_count";
#my $t = new tracker(12);
#print $white->tostring(), "\n";
# process historical data
my $db_file = "$dirname/loto_hist.db";

my @samples;
{
    my $file = $db_file;
    if( !-f "$db_file" || $download == 1)
    {
	$file = "curl http://38.121.105.10/powerball/winnums-text.txt|";
	if( $download == 1)
	{
            open FILE, "$file";
	    open OUT, ">$db_file";
            while(my $line=<FILE>)
	    {
		    print OUT $line;
	    }
	    close OUT;
	    close FILE;
	    if( -f "$db_file" )
	    {
		   $file = $db_file;
	    }
	}
    }
    open FILE, "$file";
    while(my $line=<FILE>)
    {
	if( $line =~ /^(\d\d\/\d\d\/\d\d\d\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/ )
	{
	    my ($date, $n1, $n2, $n3, $n4, $n5,$pb ) = ($1, int($2), int($3), int($4), int($5), int($6), int($7));
	    chomp $line;
	    #print $line, "\n";
	    $date =~ /\d\d\/\d\d\/(\d\d\d\d)/;
	    my $year = int($1);
	    next if ($year <= 2012);
	    push @samples, "$date;$n1;$n2;$n3;$n4;$n5;$pb";
	}
    }
    close FILE;
    @samples = reverse(@samples);
   
    while(scalar(@samples)>$sample_count)
    {
	shift @samples;
    } 

    my $i=0;
    foreach my $l(@samples)
    {
	#print "$i=$l\n";$i++;
    }
}
#die "";
my @skip;
my $skip =0;

my $white = new container("white", 1,59);
my $red   = new container("red",   1,35);
foreach my $line(@samples)
#while(my $line=<FILE>)
{
	#print "$line\n";
    #$line =~ s/=>.+//;
    chomp $line;

    if( $skip == 1)
    {
	push @skip, $line;
	next;	
    }
    my @data = split /;/, $line;
    my ($date, $n1, $n2, $n3, $n4, $n5, $pb ) = @data;
    if(defined($end_date) && ($end_date eq $date ))
    {
	print STDERR "skipping $line\n";
	push @skip, $line;
	$skip = 1;
	next;
    }
    #print "WIN $line\n";
    my @num = ( $n1, $n2, $n3, $n4, $n5);
    @num = sort { $a <=> $b } @num;
    print "WIN $date;";
    foreach my $d(@num)
    {
	    print "$d;";
    }
    print "$pb\n";
    #print "$line '$pb'\n";
    #die "$line\n$date, $n1";
    $white->age();
    $white->update_frequency(int($n1));
    $white->update_frequency(int($n2));
    $white->update_frequency(int($n3));
    $white->update_frequency(int($n4));
    $white->update_frequency(int($n5));

    $red->age();
    $red->update_frequency(int($pb));
}
print $white->tostring($sort_order), "\n";
print "RED---------\n";
print $red->tostring($sort_order), "\n";
foreach my $s(@skip)
{
    print "SKIPPED -- $s\n";
}
