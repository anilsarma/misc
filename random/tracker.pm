package tracker;
sub new($)
{
    my ($name, $number) = @_;
    my @run;
    my $self = { 'number' => $number, 'frequency' => 0, 'age' => 0, 'max' => 0, 'wt'=>0, 'run' => \@run };
    bless $self, $name;
    return $self;

}
sub get_number($)
{
    my ($self) = @_;
    return $self->{'number'};
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
1;
