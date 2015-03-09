use tracker;
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
sub get_age_trackers()
{
    my ($self,$sort) = @_;
    my %trackers = %{$self->{'tracker'}};
    my @result;
    foreach my $k ( sort { sort_trackers("age", $trackers{$a}, $trackers{$b}) } keys %trackers )
    {
	push @result, $trackers{$k};
    }
    
    return @result;
}
sub get_trackers()
{
    my ($self,$sort) = @_;
    my %trackers = %{$self->{'tracker'}};
    my @result;
    foreach my $k(sort {$a <=> $b} keys %trackers)
    {
	push @result, $trackers{$k};
    }
    
    return @result;
}
sub sort_trackers_freq_age($$)
{
    my ($a, $b) = @_;
    if( $a->get_freq() == $b->get_freq())
    {
	return $a->get_age() <=> $b->get_age()
    }
    return $a->get_freq() <=> $b->get_freq();
}
sub sort_trackers_age_freq($$)
{
    my ($a, $b) = @_;
    if( $a->get_age() == $b->get_age())
    {
	 if($b->get_freq() == $a->get_freq())
	 {
		 return $a->get_number() <=> $b->get_number();
	 }
	 return $b->get_freq() <=> $a->get_freq()
    }
    return $a->get_age() <=> $b->get_age();
}
sub sort_trackers($$$)
{
    my ($sort_order, $a, $b) = @_;
    if( defined($sort_order) && $sort_order eq "freq" )
    {
       return sort_trackers_freq_age( $a, $b );
    }
    return sort_trackers_age_freq( $a, $b );
}

sub tostring($$)
{
    my ($self, $sort_order) = @_;
    my %trackers = %{$self->{'tracker'}};
    # sorted by age.
    foreach my $k ( sort { sort_trackers($sort_order, $trackers{$a}, $trackers{$b}) } keys %trackers )
    {
	printf $self->{ball}." %02d=%s%s", $k , $trackers{$k}->tostring(), "\n";
    }
}
1;
