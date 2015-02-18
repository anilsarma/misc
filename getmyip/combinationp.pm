#!/usr/bin/perl -w 
#
use strict;

package combinationp;
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
sub combi($$)
{
	my($n, $p) = @_;
	return factorial($n)/(factorial($n-$p)*factorial($p));
}
sub print_data($$)
{
	my ($index, $data) = @_;
	my @index = @{$index};
	
	#my @data = @{$data};
	my $str = "";
	foreach my $i(@index)
	{
		$str.= "$i ";
	}
        return $str;
}
sub increment($$);
sub increment($$)
{
	my ($self, $offset) = @_;
	#my @index = @{$self->{'index'}};
	#my @data = @{$self->{'data'}};
        if($offset <0)
	{
		return -1;
	}
        my $limit = scalar(@{$self->{'data'}});
	#print "increment offset=$offset limit=$limit\n";
	$self->{'index'}->[$offset]=$self->{'index'}->[$offset] + 1;
	#print "\tincrement offset=$offset limit=$limit offset(data)[$offset]=", $self->{'index'}->[$offset], "\n";;
	if( $self->{'index'}->[$offset]>= $limit)
	{
	      $self->{'index'}->[$offset]=0;
	     if($self->increment($offset-1)==1)
	     {
	        $self->{'index'}->[$offset]=0;
	     }
	     else
	     {
		     #print "bad\n";
		     return -1;
	     }
	     if( $self->{'index'}->[$offset]>= $limit)
	     {
		     #p	rint "bad\n";
		     return -1;
	     }
	     
	}
	#print "\treturn increment offset=$offset limit=$limit offset(data)[$offset]=", $self->{'index'}->[$offset], "\n";;
	#print "\treturn data=";	combinationp::print_data($self->{'index'}, $self->{'index'});
	return 1;
}
sub next($)
{ 
     my ($self) = @_;
     #print "next::", $self->{'valid'}, "\n";
     return () if ($self->{'valid'} ==0 );
     my @ret =  @{$self->{'index'}};
     while(1)
     {
     if( $self->increment($#ret) == -1)
     {
	     #print "set valid = 0\n";
	     $self->{'valid'}=0;
	     last;
     }
        my @d = @{$self->{'index'}};
	@d = sort {$a <=> $b } @d;
	my $str = "";
	foreach my $d(@d)
	{
		 $str.=";$d";
	}
	if(!defined($self->{'used'}->{$str}))
	{
		$self->{'used'}->{$str}=$str;
		last;
	}
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
		push @index, 0;
	}
	my $len = scalar(@data);
	my $c = 5000; #combi($len + $set-1, $set );
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

package main;
my @data = (0, 1, 2, 3, 4, 5);
my @prop = ( 9, 10, 10, 10, 10, 10);
my $c = new combinationp(5, \@data);
print "total=", $c->n(), "\n";

my @l;
my $total = combinationp::combi(59,5);
my %db;
for(my $i=0; $i < $c->n(); $i++)
{
	my @ret = $c->next();
	last if ($#ret <0);
	my $p=1;
        my @tprop = @prop;
        foreach my $r(@ret)
	{
		$p = $p * $tprop[$r];
		$tprop[$r]--;
	}
        my $key = combinationp::print_data(\@ret, \@data);
	my @tmp;
	my $data = {'total'=> 0, 'records'=> \@tmp, 'data' => \@ret, 'p' => ($p/$total), 'outcomes' => $p, 'key'=> $key };
	$db {$key} = $data;
	push @l, $data;
}

sub sort_d($$)
{
	my ($a, $b) = @_;
	return  $a->{'outcomes'} <=> $b->{'outcomes'};
}
@l = sort { sort_d($a,$b)} @l;
use rfile;
use File::Spec::Functions qw(rel2abs);
use File::Basename;
my $dirname=dirname(rel2abs($0));

sub freq(@)
{
  my @data = @_;
  my @f = ();
  foreach my $d(@data)
  {
	  my $x = int(int($d)/10);
	  push @f, $x;
	  #print "fre $x\n";
  }
  return @f;
}
my $file = "$dirname/loto_hist.db";
my $r = new rfile($file);
my $tries = 0;
while (defined(my $n= $r->next() ))
{
       my $total = 0;
       my @white = $n->white();
       my @f = freq(@white);
       my $key = combinationp::print_data(\@f, undef);
       foreach my $w(@white)
       {
               $total += int($w);
	       #print "white $w\n";
       }
       #print "$key=$total\n";
       if(!defined($db{$key}->{'total'}))
       {
	       $db{$key}->{'total'}=0;
       }
       $db{$key}->{'total'}+=$total;
       push @{$db{$key}->{'records'}}, $n;
       $tries ++;
}
sub sum(@)
{
	my $total = 0;
	foreach my $s(@_)
	{
		$total += $s;
	}
	return $total;
}

foreach my $d(@l)
{
	my @records = @{$d->{'records'}};
	my $actual = scalar(@records);
	my $estimated = $tries * $d->{'p'};
	my $average = $d->{'total'};
	if($actual>0)
	{
		$average /= $actual;
	}
	print $d->{'outcomes'}, " p=", sprintf("%.2f",$d->{'p'}*100) , " tries=", $tries, " estimated=", $estimated, " acutal=", $actual, " total=", $d->{'total'}, " average=", $average, " data=",  combinationp::print_data($d->{'data'}, undef), "\n";
	foreach my $r(@records)
	{
		my @w = $r->white();
	       print "\t", combinationp::print_data(\@w, undef), "sum=", sum(@w), "\n";
	}
}
