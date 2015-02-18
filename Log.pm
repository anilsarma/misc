package Log;
use strict;
use Cwd;
use utils;
use threads;
use threads::shared;
use Thread::Queue;

sub new ( $$$ )
{
    my ($object ) = @_;

    my $self = {};
    $self->{'queue'} = new Thread::Queue();
    $self->{'live'}=1;
    bless $self;

    #
    $self->{'tid'} = threads->create( \&entryPoint, $self );
    return $self;

}

sub entryPoint
{
    my ($self) = @_;
    my $queue = $self->{'queue'};
    while( $self->{'live'}==1 )
    {
        #print "In msg loop",  $self->{'live'}, "\n";
        my @msg= $queue->dequeue();
        foreach my $m ( @msg )
        {
            return if ( !defined($m) );
            print  $m;
        }
    }
    #print STDERR "entryPoint: done\n";
}

sub close()
{
    my $self = shift;
    $self->{'live'}=0;
    #print STDERR "setting live =0\n";
    $self->{'queue'}->enqueue(undef);
    $self->{'tid'}->join();
}
sub log()
{
    my $self = shift;
    $self->{'queue'}->enqueue( @_ );

}
sub DESTROY {
    my $self = shift;
    #printf("$self dying at %s\n", scalar localtime);
    #$self->close();
}
1;
