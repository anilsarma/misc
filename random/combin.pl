use combination;
my @data = @ARGV;
my $c = new combination(5, \@data);
print "total=", $c->n(), "\n";
for(my $i=0; $i < $c->n(); $i++)
{
       my @ret = $c->next();
        print $i, " data=";    combination::print_data(\@ret, \@data);
}

