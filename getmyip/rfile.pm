#!/usr/bin/perl -w

use strict;
use File::Spec::Functions qw(rel2abs);
use File::Basename;

package db_entry;
sub new($$$$$$$$)
{
    my ($name, $date, $n1, $n2, $n3, $n4, $n5, $pb ) = @_;
    my @white= ($n1, $n2, $n3, $n4, $n5 );
    @white = sort { $a <=> $b } @white;
    my $self = { 'white' => \@white, 'red' => $pb, 'date' => $date };

    bless $self, $name;
    return $self;
}
    
sub date($)
{
    my ($self) = @_;
    return $self->{'date'};
}

sub white($)
{
    my ($self) = @_;
    return @{$self->{'white'}};
}
sub red($)
{
    my ($self) = @_;
    return $self->{'red'};
}

    
package rfile;
sub new($$)
{
    my ($name, $file) = @_;
    
    my $self = { 'name'=> $name, 'file' => $file };
    my @samples;
    
    if( !-f "$file" )
    {
	die "cannot open file $file";
	
    }
    else
    {
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
		my @white= ($n1, $n2, $n3, $n4, $n5 );
		#my %data = { 'white' => \@white, 'red' => $pb, 'date' => $date };
		my $e = new db_entry( $date, $n1, $n2, $n3, $n4, $n5,$pb );
		push @samples, $e;
	    }
	}
	close FILE;
    }
    @samples = reverse(@samples);
    $self->{'samples'} = \@samples;
    $self->{'index'} = 0;
    bless $self, $name;
    return $self;
}

sub next($)
{
    my ($self) = @_;
    my $i = $self->{'index'};
    if( $i <= scalar(@{$self->{'samples'}}))
    {
	$self->{'index'} ++;
	return $self->{'samples'}->[$i];
    }
    return undef;
}
1;
