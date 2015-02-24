#!/usr/bin/perl -w 
BEGIN
{
    use File::Spec::Functions qw(rel2abs);
    use File::Basename;
    my $dirname=dirname(rel2abs($0));
    push @INC, $dirname;
}
#
use strict;

use combination;

use File::Spec::Functions qw(rel2abs);
use File::Basename;
my $dirname=dirname(rel2abs($0));
#die "$sample_count";
##my $t = new tracker(12);
##print $white->tostring(), "\n";
## process historical data
my $db_file = "$dirname/loto_hist.db";


open FILE, $db_file;
my @samples;
my @records;
while( my $line = <FILE>)
{
	if( $line =~ /^(\d\d\/\d\d\/\d\d\d\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/ )
	{
	    my ($date, $n1, $n2, $n3, $n4, $n5,$pb ) = ($1, int($2), int($3), int($4), int($5), int($6), int($7));
	    chomp $line;
	    $date =~ /\d\d\/\d\d\/(\d\d\d\d)/;
	    my $year = int($1);
	    my @data = ($n1, $n2, $n3, $n4, $n5 );
	    @data = sort {$a <=> $b } @data;
	    next if ($year <= 2012);
	    push @samples, "$date;$n1;$n2;$n3;$n4;$n5;$pb";
	    my $record = { 'data' => \@data, 'line'=> $line, 'date' => $date, 'pb'=>$pb };
	    push @records, $record;
	}
}
close FILE;


my %statistics;
for( my $i=2;$i <=5; $i ++ )
{
    foreach my $r(@records)
    {
	my @data = @{$r->{'data'}};
	my $c = new combination($i, \@data);
	while(scalar(my @d = $c->next())>0)
	{
	    #combination::print_data(@d, @d);
	    my $str = "";
	    foreach my $d(@d)
	    {
		$str .= "$d ";
	    }
	    #print "$str\n";
	    $statistics{$i}{$str} ++;
	    
	}
	
    }
    my $count = 0;
    foreach my $s(keys $statistics{$i})
    {
	my $d = $statistics{$i}{$s};
	#print $s, "=",$d, "\n" if($d>1);
	$count += ($d-1) if ($d>1);
    }
    print "statistics $i count=$count\n";
}
#my @data = ( 23, 24, 25, 26, 27 );

print "compared with current nyumber\n";
my @data = @ARGV;
@data = sort {$a <=> $b } @data;
for( my $i=2;$i <=5; $i ++ )
{
    foreach my $s(keys $statistics{$i})
    {
	$statistics{$i}{$s}=0;
    }
}
for( my $i=2;$i <=5; $i ++ )
{
    my $c = new combination($i, \@data);
    while(scalar(my @d = $c->next())>0)
    {
	#combination::print_data(\@d, \@d);
	my $str = "";
	foreach my $d(@d)
	{
	    $str .= "$d ";
	}
	#print "$str\n";
	$statistics{$i}{$str} ++ if( defined($statistics{$i}{$str}));
    }
    my $count = 0;
    foreach my $s(keys $statistics{$i})
    {
	my $d = $statistics{$i}{$s};
	#print $s, "=",$d, "\n" if($d>1);
	$count += $d  if ($d>0);
    }
    print "statistics $i count=$count\n";
}
