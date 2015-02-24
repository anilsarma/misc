#!/usr/bin/perl -w 
#
use strict;

package combination;
sub factorial ($);
sub factorial ($)
{
	my ($n) = @_;
	if($n == 1 || $n==0)
	{
		return 1;
	}
	return $n * factorial($n-1);
}

sub print_data($$)
{
	my ($index, $data) = @_;
	my @index = @{$index};
	my @data = @{$data};
	foreach my $i(@index)
	{
		print "$i ";
	}
	print "\n";
}
sub increment($$);
sub increment($$)
{
	my ($self, $offset) = @_;
	my @index = @{$self->{'index'}};
	my @data = @{$self->{'data'}};
        if($offset <0)
	{
		return -1;
	}
	my $l = scalar(@data);
        my $limit = scalar(@data)- scalar(@index)+$offset;
	#print "increment offset=$offset limit=$limit\n";
	$self->{'index'}->[$offset]=$self->{'index'}->[$offset] + 1;
	#print "\tincrement offset=$offset limit=$limit offset(data)[$offset]=", $index->[$offset], "\n";;
	if( $self->{'index'}->[$offset]> $limit)
	{
	     if($self->increment($offset-1)==1)
	     {
	        $self->{'index'}->[$offset]=$self->{'index'}->[$offset-1]+1;
	     }
	     else
	     {
		     #print "bad\n";
		     return -1;
	     }
	     if( $self->{'index'}->[$offset]> $limit)
	     {
		     #print "bad\n";
		     return -1;
	     }
	     
	}
	return 1;
}
sub next($)
{ 
     my ($self) = @_;
     #$print "next::", $self->{'valid'}, "\n";
     return () if ($self->{'valid'} ==0 );
     my @ret =  @{$self->{'index'}};
     if( $self->increment($#ret) == -1)
     {
	     #print "set valid = 0\n";
	     $self->{'valid'}=0;
     }
     my @r = ();
     foreach my $x(@ret)
     {
	  push @r, $self->{'data'}->[$x];
     }
     return @r;
}
 

sub new($$$)
{
	my($name, $set, $data ) = @_;
	my @data = @{$data};
	my @index;
	for(my $i=0; $i < $set ;$i++)
	{
		push @index, $i;
	}
	my $len = scalar(@data);
	my $c = factorial($len)/( factorial($len-$set)*factorial($set));
	#print $c, "\n";
	my $this = { 'index' => \@index, 'data' => \@data, 'n' => $c, 'valid' => 1 };
	#for(my $i=0; $i < $c+1; $i++)
	#{
		#	print_data(\@index, \@data);

		#increment(\@index, \@data, $#index);
		#}
	bless $this, $name;
	return $this;
}

sub n($)
{
	my ($self) = @_;
	return $self->{'n'};
}
1;

#package main;
#my @data = (221, 2, 3, 4, 5, 6);
#my $c = new combination(3, \@data);
#print "total=", $c->n(), "\n";
#for(my $i=0; $i < $c->n(); $i++)
#{
#	my @ret = $c->next();
#        print $i, " data=";	combination::print_data(\@ret, \@data);
#}

