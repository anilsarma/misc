package color;

use utils;
my $console = 1;
my $COLOR_RESET=0;
#//export ANSI_ATTR_BRIGHT=1
#//export ANSI_ATTR_DIM=2
#//export ANSI_ATTR_UNDERSCORE=4
#export ANSI_ATTR_BLINK=5
#export ANSI_ATTR_REVERSE=7
#export ANSI_ATTR_HIDDEN=8

my $COLOR_FG_BLACK=30;
my $COLOR_FG_RED=31;
my $COLOR_FG_GREEN=32;
my $COLOR_FG_YELLOW=33;
my $COLOR_FG_BLUE=34;
my $COLOR_FG_MAGENTA=35;
my $COLOR_FG_CYAN=36;
my $COLOR_FG_WHITE=37;

my $COLOR_BG_BLACK=40;
my $COLOR_BG_RED=41;
my $COLOR_BG_GREEN=42;
my $COLOR_BG_YELLOW=43;
my $COLOR_BG_BLUE=44;
my $COLOR_BG_MAGENTA=45;
my $COLOR_BG_CYAN=46;
my $COLOR_BG_WHITE=47;


my $ptty = undef;
sub console()
{
    if( !utils::is_win() )
    {
        if( !defined($ptty) )
        {
            my $out = `tty 2>&1`;
            chomp $out;
            my $ret  = $?;

            if( $ret == 0 )
            {
                $ptty = 1;
            }
            else
            {
                $ptty = 0;
            }
            #print STDERR "console(): $out $ptty\n";
        }
    }
    if( $ptty == 0 )
    {
        return 0;
    }
    return $console;
}

sub set_console ( $ )
{
    my ($value) = @_;
    $console = int( $value );
}

sub color( @ )
{
    my @c = @_;
    my $str = "[0];
    shift @c;
    foreach my $c ( @c )
    {
        $str .= ";$c";
    }
    $str .= "m";
    return $str;
}
sub red( $)
{
    my ($msg) =@_;
    #print "OLOR_FG_RED"."m$msg"."";
    return $msg if ( console() != 1 );
    return color($COLOR_FG_RED) . $msg . color($COLOR_RESET);
}
sub blue( $)
{
    my ($msg) =@_;
    #print "OLOR_FG_RED"."m$msg"."";
    return $msg if ( console() != 1 );
    return color($COLOR_FG_BLUE) . $msg . color($COLOR_RESET);
}
sub green( $)
{
    my ($msg) =@_;
    #print "OLOR_FG_RED"."m$msg"."";
    return $msg if ( console() != 1 );
    return color($COLOR_FG_GREEN) . $msg . color($COLOR_RESET);
}

1;
