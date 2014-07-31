#!/usr/bin/perl -w
use strict;

my @hosts = ( "ifconfig.me", "icanhazip.com", "ident.me", "ipecho.net/plain", "whatismyip.akamai.com", "tnx.nl/ip", "myip.dnsomatic.com", "ip.appspot.com", "checkip.dyndns.org" ); 
my $path = "<some path>/router_check";
my $ipstore = "$path/ip.data";

my $gmail = "<some util to send meail>  \"Route IP Changed\" ";

#foreach my $h(@hosts)
for(my $i=0; $i < $#hosts + 1; $i ++ )
{
    my $random_number = rand()*100000;
    my $index = $random_number % ($#hosts +1);
    print "random $random_number\n";
    my $h = $hosts[$index];
    {
	my $m=`curl -s $h`;
	if( $m =~ /(\d+\.\d+\.\d+\.\d+)/ )
	{
	    my $ip = $1;
	    print "ip:$ip => $h\n";
	    my $lastip = "";
	    $lastip = `cat $ipstore` if ( -f $ipstore );
	    chomp $lastip;
	    if( $lastip ne $ip )
	    {
		my $time = `date`;chomp $time;
		print "$time: ip has changed to $ip from $lastip file $ipstore using host $h attempt=$i\n";
		open  OFILE, ">$ipstore";
		print OFILE "$ip";
		close OFILE;
		my $old = "";
		if( length($lastip) > 0 )
		{
		    $old = "changed from $lastip";
		}
		system "$gmail \"$time: New IP Address is $ip $old using host $h attempt=$i\"";
	    } 
            exit(0);
	    last;
	}
    }
}
