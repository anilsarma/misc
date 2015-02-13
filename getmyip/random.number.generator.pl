#!/usr/bin/perl -w
use Getopt::Long;
use strict;
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

package tracker;
sub new($)
{
    my ($name, $number) = @_;
    my @run;
    my $self = { 'number' => $number, 'frequency' => 0, 'age' => 0, 'max' => 0, 'wt'=>0, 'run' => \@run };
    bless $self, $name;
    return $self;

}
sub incr_age($)
{
    my ($self) = @_;
    $self->{'age'}++;
    if( $self->{'age'} > $self->{'max'} )
    {
	$self->{'max'} = $self->{'age'};
    }
    return $self->{'age'};
}
sub incr_freq($)
{
    my ($self) = @_;
    $self->{'frequency'}++;  
    $self->{'wt'}++;
    return $self->{'frequency'};
}
sub set_age($$)
{
    my ($self,$age) = @_;
    if( $age == 0 && ($self->{'frequency'}>0) )
    {
	push @{$self->{'run'}},$self->{'age'}; 
    }
    $self->{'age'} = $age;
}
sub set_freq($$)
{
    my ($self,$frequencey) = @_;
    $self->{'frequency'}= $frequencey;
}
sub get_age($)
{
    my ($self) = @_;
    return $self->{'age'};
}
sub get_freq($)
{
    my ($self) = @_;
    return $self->{'frequency'};
}
sub tostring($)
{
    my ($self) = @_;
    my $run="";
    my $rc=0.0;
    my $rt=0;
    foreach my $r(@{$self->{'run'}})
    {
	$run .= " $r";
	$rt += int($r);
	$rc= $rc + 1;
    }
    if($rt>0)
    {
	$rc =$rt/$rc;
    }
    my $src = sprintf("%.2f", $rc );
    my $str =  "[" . "number=" . sprintf("%02d", int($self->{'number'}));
    $str .= sprintf(" age=%03d", int($self->{'age'}));
    $str .= sprintf(" frequency=%03d", $self->{'frequency'});
    #$str .= sprintf(" wt=%03d", $self->{'wt'});
    $str .= sprintf(" max=%03d", $self->{'max'});

    my $delta =  $rc - int($self->{'age'});
    my $sdelta = sprintf("%.2f", $delta );

    $str .= sprintf(" delta=%7.2f", $delta);
    $str .= " run=($run )~$src ". "]";
    return $str;
}

package container;
sub new($$$$)
{
    my ($name, $ball,$start, $end) = @_;

    my %trackers;
    for(my $i=$start;$i <= $end; $i++)
    {
	my $t = new tracker($i);
	$trackers{$i} =  $t;
    }

    my $self = { 'ball'=>$ball, 'start' => $start, 'end' => $end, 'tracker' => \%trackers  };
    bless $self, $name;
    return $self;
}
# age everything.
sub age($)
{
    my ($self) = @_;
    my %trackers = %{$self->{'tracker'}};
    foreach my $k ( sort {$a <=> $b} keys %trackers )
    {
	$trackers{$k}->incr_age();
    }
}
# age everything.
sub set_age($$$)
{
    my ($self,$number,$age) = @_;
    my %trackers = %{$self->{'tracker'}};
    
    $trackers{$number}->set_age($age);
    
}
sub update_frequency($$)
{
    my ($self,$number) = @_;
    my %trackers = %{$self->{'tracker'}};
    #print "Num=$number\n";
    $trackers{$number}->incr_freq();
    $trackers{$number}->set_age(0);
}
sub get_trackers()
{
    my ($self) = @_;
    my %trackers = %{$self->{'tracker'}};
    return \%trackers;
}
sub sort_trackers($$)
{
    my ($a, $b) = @_;
    if( $a->get_age() == $b->get_age())
    {
	$b->get_freq() <=> $a->get_freq()
    }
    return $a->get_age() <=> $b->get_age();
}

sub tostring($)
{
    my ($self) = @_;
    my %trackers = %{$self->{'tracker'}};
    # sorted by age.
    foreach my $k ( sort { sort_trackers($trackers{$a}, $trackers{$b}) } keys %trackers )
    {
	printf $self->{ball}." %02d=%s%s", $k , $trackers{$k}->tostring(), "\n";
    }
}
package main;
my $DEFAULT_SAMPLE_COUNT=100000; #120; # 2 years
my $sample_count = $DEFAULT_SAMPLE_COUNT;
my $end_date = undef;
sub usage($)
{
    my ($msg) = @_;
#Usage: omm-app.sh: [-l mini1|mini2|conlab|simlab] -e <executable> -d [use development, default is build ] -t <topdir> -r <lab-config-root> -b <buildir> -o <
    print STDERR "error: $msg\n" if (defined($msg));
    print STDERR "usage: $program_name <options> \n";
    print STDERR "\tversion:\n";
    print STDERR "options:\n";
    print STDERR "       -samples <sample count>  total number of samples to use default $DEFAULT_SAMPLE_COUNT\n";
    print STDERR "       -end  <date>             all samples before this date\n";
    exit(0);
}
GetOptions(  "help"           =>   sub { usage(undef); },
	     "samples=s"      => \$sample_count,
	     "end_date=s"     => \$end_date,
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
    if( !-f "$db_file")
    {
	#print "PIPE\n";
	$file = "curl http://38.121.105.10/powerball/winnums-text.txt|";
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
    print "$line\n";
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
    print "$line\n";
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
print $white->tostring(), "\n";
print "RED---------\n";
print $red->tostring(), "\n";
foreach my $s(@skip)
{
    print "SKIPPED -- $s\n";
}
