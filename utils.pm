
package utils;
use Digest::MD5;
use Cwd;
use Config;
use Data::Dumper;
use IO::File;
use Time::Local;
use MIME::Base64;
sub dirname( $ )
{
    my ($cmd) = @_;

    $cmd = make_linux_path( $cmd );

    $cmd =~ s/\/[^\/]+$//;
    return $cmd;
}

sub filename( $ )
{
    my ($cmd) = @_;

    if(!defined($cmd) )
    {
        return undef;
    }

    $cmd = make_linux_path( $cmd );
    if($cmd =~ s/\/([^\/]+)$//g)
    {
        #print "XX=>$1'";
        return $1;
    }
    return $cmd;
}
sub ucFirst ( $ )
{
    my ($tmp) = @_;

    my $first = substr( $tmp, 0, 1 );
    my $remain = substr( $tmp, 1 );

    return  uc( $first ).$remain;
}
sub lcFirst ( $ )
{
    my ($tmp) = @_;

    my $first = substr( $tmp, 0, 1 );
    my $remain = substr( $tmp, 1 );

    return lc( $first ).$remain;
}


# current time in seconds.
sub current_time()
{

    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
    my $time = $hour * 60 * 60 + $min * 60 + $sec;
    return $time;
}

sub make_printable_time($)
{
    my ($time) = @_;
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
    my $ptime = $hour * 60 * 60 + $min * 60 + $sec;
    $ptime *= 1000;
    return sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $mday ). " ". make_formated_time($ptime);
}

sub printable_date()
{
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
    #my $ptime = $hour * 60 * 60 + $min * 60 + $sec;
    #$ptime *= 1000;
    return sprintf("%04d%02d%02d", $year + 1900, $mon + 1, $mday );
}

# all time returend in micros
sub parse_formated_time($)
{
    my ($timeorig ) = @_;
    if( $timeorig =~ /(\d+):(\d+):(\d+)\.(\d+):?/ )
    {
        my ($hr, $min, $sec, $mili) = ( $1, $2, $3, $4 );
        my $micro = 0;
        if( length("$mili") > 3 )
        {
            $micro  = 1;
        }
        my $time = $hr * 60 * 60 * 1000 + $min * 60 * 1000 + $sec * 1000 ;
        if( $micro == 0 )
        {
            $time += int($mili);
            $time *= 1000;
        }
        else
        {
            $time *=1000; # convert to micro
            $time += int($mili); # actually micro


            #die "$timeorig milli=$mili len=" . length($mili);
        }
        #print "$time\n";
        #exit(0);
        return ($time, $hr, $min, $sec, $mili );
    }
    return undef;
}


sub make_formated_time( $ )
{
    my ($time ) = @_;

    my $micro = $time%1000000; $time /= 1000000;
    my $sec  = $time%60; $time /= 60;
    my $min  = $time%60; $time /= 60;
    my $hr   = $time;

    return ( $hr, $min, $sec, $micro, sprintf("%02d:%02d:%02d.%06d",$hr, $min, $sec, $micro) );
}

sub make_time( $ )
{
    my ($time) = @_;

    if( $time !~ /^(\d+):(\d+):(\d+)\.(\d+)$/ )
    {
        if( $time =~ /^(\d+)$/ )
        {
            $time = $time.":00:00.00";
        }
        elsif( $time =~ /^(\d+):(\d+)$/ )
        {
            $time = $time.":00.00";
        }
        elsif( $time =~ /^(\d+):(\d+):(\d+)$/ )
        {
            $time = $time.".00";
        }
        else
        {
            die "bad time $time ";
            return undef;
        }
    }
    return $time;
}


sub checksum ( $ )
{
    my ($file) = @_;
    my $d = new Digest::MD5();
    open DFILE, "$file" ||  die "cannot open file $file";
    while( my $line=<DFILE> )
    {
        $d->add( $line );
    }
    close DFILE;
    return $d->hexdigest;
}

sub copy_file ( $$ )
{
    my ($src, $dest) = @_;

    my $sf = new IO::File( $src );
    my $df = new IO::File( ">$dest" );
    #open DFILE, "$file" ||  die "cannot open file $file";
    while( my $line=<$sf> )
    {
        print $df $line;
    }
    $sf->close();
    $df->close();
}

sub stacktrace_print  ()
{
    my ( $path, $line, $subr );
    my $max_depth = 30;
    my $i = 0;
    my $str = "";
    #if ($log->is_warn())
    {
        $str .= "--- Begin stack trace ---\n";
        while ( (my @call_details = (caller($i++))) && ($i<$max_depth) )
        {
            my ($package, $filename, $line, $subroutine, $hasargs,
                $wantarray, $evaltext, $is_require, $hints, $bitmask)  =@call_details;

            $str .=  "$filename:$line:$subroutine\n" if (defined($line));
        }
        $str .= "--- End stack trace ---\n";
    }
    return $str;
}
sub stacktrace  ()
{
    print STDERR stacktrace_print();
}
sub stacktrace_die ($)
{
    my ($msg) = @_;
    print STDERR "$msg\n";
    stacktrace();
    die "\n";
}
sub createdb ()
{
    my %ttmp;
    my @tmp;
    my %tmp = ( 'hash' => \%ttmp, 'dir' =>  \@tmp );
    my $db = \%tmp;
    return $db;
}
sub find_uniqe_directory ( $$$ );
sub find_uniqe_directory ( $$$ )
{
    my ( $db, $dir, $pattern ) = @_;

    my $root = 0;
    if( !defined($db) )
    {
        $root = 1;
        $db = createdb();
    }
    $dir = make_os_path($dir);
    {
        my @tmp;
        if( ! -d "$dir" )
        {
            return @tmp;
        }
    }
    #print STDERR "find_unique_dir:$dir\n";
    opendir DIR, $dir;
    my @content = readdir DIR;
    closedir DIR;

    my @dir;
    foreach my  $value ( @content )
    {
        if( $value !~ /^\.\.?$/ )
        {
            push @dir, "$dir/$value" if ( -d "$dir/$value" );
            if ( -f "$dir/$value" )
            {
                if ( "$value" =~ /$pattern/ )
                {
                    my $hash = $db->{'hash'};
                    if( !exists( $hash->{$dir} ) )
                    {
                        $hash->{$dir} = $dir;
                        $dir =~ s/\/\//\//g;
                        push @{$db->{'dir'}}, $dir;
                        last; # don't need to check files for this directory anymore.
                    }
                }
            }
        }
    }

    foreach my $d( @dir )
    {
#       print "$d\n";
       my $cwd = getcwd();
       chdir $dir;
       my $name = utils::filename( $dir );
       my $dirname = utils::dirname( $dir );
       #print "$dir ==> $name\n" if(!defined($name));
       if( defined($name) &&  -l $name )
       {
           my $slink = readlink ( $dir );
           chdir $cwd;

           my $nname = utils::filename( $dirname );
           next if( $name eq $nname);
       }
       chdir $cwd;
       find_uniqe_directory( $db, $d, $pattern );
    }

    if( $root == 1 )
    {
        return @{$db->{'dir'}};
    }
}

sub find_pattern( @ )
{
    my ($pattern) = @_; shift;
    my ( $dir ) = @_;
    my $lddb = createdb();
    #my $pattern = "lib\.+?.so\$";
    foreach my $dir ( @_ )
    {
        find_uniqe_directory( $lddb, $dir, $pattern);
    }

    my @dir =  @{$lddb->{'dir'}};
    my %dir;
    my @result;
    foreach my $dir (@dir)
    {
         if( !exists($dir{$dir}))
         {
             $dir{$dir} = $dir;
             push @result, $dir;
         }
    }
    return @result;
}

# check if the directory contains a dir matching pattern.
sub find_dir_pattern( $$ );
sub find_dir_pattern( $$ )
{
    my ( $pattern, $dir ) = @_;
    my $root = 0;

    $dir = make_os_path($dir);
    {
        my @tmp;
        if( ! -d "$dir" )
        {
            #print STDERR "$dir\n";
            return undef;
        }
    }
    opendir DIR, $dir;
    my @content = readdir DIR;
    closedir DIR;

    my @dir;
    foreach my  $value ( @content )
    {
        if( $value !~ /^\.\.?$/ )
        {
            push @dir, "$dir/$value" if ( -d "$dir/$value" );


            if( $value =~ /$pattern/ )
            {
                return "$dir/$value";
            }
            #die "bad pattern $pattern " if ($value =~ /generated/);
        }
    }
    foreach my $d (@dir )
    {
        my $result = find_dir_pattern($pattern, $d );
        if(defined($result) )
        {

            return $result;
        }
    }

    #print STDERR "$dir\n";
    return undef;

}
sub get_os()
{
    return  "$Config{'osname'}";
}

sub get_os_delimit()
{
    my $delimit = ";";
    if( uc(get_os()) eq "MSWIN32" )
    {
        $delimit = "&&";
    }
    return $delimit;
}
sub is_win()
{
    if( get_os() =~ /WIN/i)
    {
        return 1;
    }
    return 0;

}
sub make_os_path( $ )
{
    my ($path) = @_;

    if( is_win() )
    {
        return make_win_path($path);
    }
    else
    {
        return make_linux_path($path);
    }
    return $path;
}

sub make_linux_path( $ )
{
    my ($path) = @_;

    if( !defined($path) )
    {
        stacktrace();
        die "argument not defined ";
    }
    $path =~ s/\\/\//g;

    return $path;
}

sub make_win_path( $ )
{
    my ($path) = @_;

    $path =~ s/\//\\/g;
    return $path;
}

sub file_exist( $ )
{
    my ($path) = @_;
    return -f make_os_path( $path);
}

sub get_home(  )
{
    my $id = `id -un`;
    chomp $id;
    my $ypcat = `ypcat passwd| grep $id`;
    chomp $ypcat;
    my $var =':';
    my @elements = split /$var/, $ypcat;
    if( $#elements >=4 )
    {
        #foreach my $a (@elements )
        #{
        #    print "$a\n";
        #}
        return $elements[5];
    }
    return $ENV{'HOME'};
}

sub get_today()
{

    my ($sec,$min,$hour,$mday,$mon,$year,
        $wday,$yday,$isdst) = localtime time;

    $year = int($year) + 1900;
    $mon = int($mon) +1;

    my $today = $year * 10000 + $mon * 100 + $mday;
    return $today;
}
sub get_today_details()
{

    my ($sec,$min,$hour,$mday,$mon,$year,
        $wday,$yday,$isdst) = localtime time;

    $year = int($year) + 1900;
    $mon = int($mon) +1;

    my $today = $year * 10000 + $mon * 100 + $mday;
    return ($year, $mon, $mday );
}

sub abs_path( $ )
{
    my ($file) = @_;

    if( !-f "$file" && !-d "$file" )
    {
        # for windows.
        if( is_win() )
        {
            return private_abs_path( $file );
            #stacktrace_die "cannot find $file";
        }
    }
    my $tmp = Cwd::abs_path( $file );
    if( !defined($tmp) )
    {
        # we need to convert this manually
        return private_abs_path( $file );
    }
    return $tmp;
}


sub private_abs_path( $ )
{
    my ($file) = @_;
    # assume linux
    $file = make_linux_path( $file );
    if( $file =~ /^\// && ( $file !~ /\/\.\.?\// || $file !~ /\/\.\.?$/) )
    {
        return $file;
    }
    if( is_win() )
    {
        if( $file =~ /[A-Za-z]:\// && ( $file !~ /\/\.\.?\// || $file !~ /\/\.\.?$/) )
        {
            return $file;
        }
    }

    warn "utils::abs_path not yet implemented $file";
    return $file;
}


sub find_file ( $$$ );
sub find_file ( $$$ )
{
    my ( $dir, $file, $ex ) = @_;
    opendir DIR, $dir || return undef;
    my @dir = readdir DIR;
    closedir DIR;

    #rint "DEBUG:(find_file) $dir $file\n";
    if(!defined($ex) )
    {
        return abs_path("$dir/$file") if ( -f "$dir/$file" );
    }
    my @dir_list;
    foreach my $d (@dir )
    {
        next if ( $d =~ /^\.\.?$/);
        if ( -d "$dir/$d")
        {
            push @dir_list, "$dir/$d";
            print "checking dir  $dir/$d\n" if ( defined($ex) );;
        }
        else
        {
            print "checking file $dir/$d\n" if ( defined($ex) );
        }


        if( $d eq $file && -x "$dir/$d" && -f "$dir/$d" )
        {
            return abs_path("$dir/$d");
        }
    }
    foreach my $d(@dir_list)
    {
        print "checking dir $d\n"if ( defined($ex));
        my $f =  find_file ( $d, $file, $ex );
        return abs_path($f) if( defined( $f) );
    }
    return undef;
}


sub _get_dir_content ( $$ );
sub _get_dir_content ( $$ )
{
    my ( $cache, $dir ) = @_;

    opendir DIR, $dir || return undef;
    my @dir = readdir DIR;
    closedir DIR;
    #print "DIR_CONEENT: $dir\n";

    my @dir_list;
    foreach my $d (@dir )
    {
        next if ( $d =~ /^\.\.?$/);
        if ( -d "$dir/$d")
        {
            push @dir_list, "$dir/$d";
        }

        if(  -f "$dir/$d" )
        {
            push @{$cache}, "$dir/$d";
        }
    }
    foreach my $d(@dir_list)
    {
        my $f =  _get_dir_content ( $cache, $d);
    }
}
sub get_dir_content ( $ )
{
    my ( $dir ) = @_;

    my @cache;
    _get_dir_content( \@cache, abs_path($dir) );
    return @cache;
}


sub _get_dir ( $$ );
sub _get_dir ( $$ )
{
    my ( $cache, $dir ) = @_;

    opendir DIR, $dir || return undef;
    my @dir = readdir DIR;
    closedir DIR;
    #print "DIR_CONEENT: $dir\n";

    my @dir_list;
    foreach my $d (@dir )
    {
        next if ( $d =~ /^\.\.?$/);
        if ( -d "$dir/$d")
        {
            push @dir_list, "$dir/$d";
            push @{$cache}, "$dir/$d";
        }

    }
    foreach my $d(@dir_list)
    {
        _get_dir ( $cache, $d);
    }
}

sub get_dir ( $ )
{
    my ( $dir ) = @_;

    my @cache;
    _get_dir( \@cache, abs_path($dir) );
    return @cache;
}

sub find_named_file ( $$ );
sub find_named_file ( $$ )
{
    my ($dir, $name) = @_;

    $dir = Cwd::abs_path($dir);
    print STDERR "$dir\n";

    if ( -d utils::make_os_path( $dir ) )
    {
        if( -f utils::make_os_path("$dir/$name" ) )
        {
            return "$dir/$name";
        }
    }

    my $ndir = utils::dirname( $dir );

    if( length($ndir) == 0 )
    {
        $ndir = "/";
    }
    if( $ndir eq $dir )
    {
        return undef;
    }
    print  STDERR "NEW $ndir\n";
    return find_named_file( $ndir, $name );
}


# if regex is defined then $name is regex
sub find_files_matching( $$$ );
sub find_files_matching( $$$ )
{
    my ($dir, $name, $regex) = @_;
    #print "DIR=$dir\n";
    my @files = get_dir_content ( $dir );
    my @result;
    foreach my $f ( @files )
    {

        my $filename = utils::filename($f);
        my $match = 0;
        if( defined($regex) )
        {
            #print "checking $f with $regex $name\n";
            if( $filename =~ /$name/ )
            {
                #print STDERR "find_files_matching: MATCH $f with $regex $name\n";
                $match = 1;
            }
        }
        else
        {
           #print "checking $f with  $name\n";

            if( length($filename)>= length($name) )
            {
                if( substr($filename, 0, length($name) ) eq $name )
                {
                    #print STDERR "find_files_matching: MATCH $f with $name\n";
                    $match = 1;
                }
            }
        }
        if( $match == 1 )
        {
            push @result, $f;
        }


    }
    return @result;
}
# if regex is defined then $name is regex
sub find_dirs_matching( $$$ );
sub find_dirs_matching( $$$ )
{
    my ($dir, $name, $regex) = @_;
    #print "DIR=$dir\n";
    my @files = get_dir ( $dir );
    my @result;
    foreach my $f ( @files )
    {

        my $filename = utils::filename($f);
        my $match = 0;
        if( defined($regex) )
        {
            #print "checking $f with $regex $name\n";
            if( $filename =~ /$name/ )
            {
                #print STDERR "find_files_matching: MATCH $f with $regex $name\n";
                $match = 1;
            }
        }
        else
        {
            #print "checking $f with  $name\n";

            if( length($filename)>= length($name) )
            {
                if( substr($filename, 0, length($name) ) eq $name )
                {
                    #print STDERR "find_files_matching: MATCH $f with $name\n";
                    $match = 1;
                }
            }
        }
        if( $match == 1 )
        {
            push @result, $f;
        }


    }
    return @result;
}
sub marshall( $$ )
{
    my ($file, $class ) = @_;
    open SFILE, ">$file" || stacktrace_die "cannot open file for writing $file";
    print SFILE Data::Dumper::Dumper( $class );
    close SFILE;
}

sub unmarshall( $ )
{
    my ($file) = @_;
    return undef if ( !-f "$file" );
    open SFILE, "$file";
    my @tmp = <SFILE>;
    close SFILE;

    #
    my $VAR1;
    my $tmp = join " ", @tmp;
    eval ( $tmp );
    return $VAR1;

}
sub get_file_content( $ )
{
    my ($file) = @_;
    my $sf = new IO::File( $file );
    print "$file\n";
    my @c = <$sf>;
    $sf->close();
    return @c;
}

sub usleep($)
{
    my ($time) = @_;
    select( undef, undef, undef, 1.0/1000.0 * $time );
}

sub process_cmd( $$ )
{
    my ($die, $cmd) = @_;

    my $mcmd = "( $cmd;echo \$? ) 2>&1 |";
    my $delimit = ";";
    if( uc(utils::get_os()) eq "MSWIN32" )
    {
        $mcmd = "( $cmd )|";
        $delimit = "&&";
    }


    print "Execututing cmd:\n$cmd => $mcmd\n";
    open PIPE,  $mcmd;
    my $last = "";
    my $retcode = 0;
    while ( my $line =<PIPE>)
    {
        chomp $line;

        my $pline = $line;
        if( $line =~ /(Can\'t.+?file) (.+)/ )
        {
            $pline = "$2:0:warning:$1";
        }


        if( $pline =~ /cannot create regular file/)
        {
            $retcode = 1; # we need to faile this process.
        }
        print $pline. "\n";

        $last = $line;
    }
    if( $retcode != 0 )
    {
        if( $die ==1 )
        {
            die "compile failed $cmd";
        }
        else
        {
            print "compile failed $cmd\n";
            close PIPE;
            return $retcode;
        }
    }
    close PIPE;
    #print "LAST=$last";
    if( uc(utils::get_os()) ne "MSWIN32" )
    {
        my $ret =  int($last);
        if( $ret != 0)
        {
            if( $die ==1 )
            {
                die "Compiled failed ";
            }
            else
            {
                print "compile failed\n";
                return $ret;
            }
        }
    }
    return 0;
}
sub open_file( $ )
{
    my ($file) = @_;
    if( $file =~ /\.gz$/ )
    {
        $file = "gzip -dc $file|";
    }
    return new IO::File($file);
}

sub read_csv_file ($)
{
    my ($file) = @_;
    my $h = open_file( $file );

    my @records;
    my $header = <$h>;
    chomp $header;

    my @names = split/[,;]/, $header;
    #print scalar(@names), "\n";
    pop @names if ( scalar(@names)> 32);
    my $lineno =0;
    while( my $line = <$h> )
    {
        $lineno++;
        chomp $line;
        my @tokens = split /,/, $line;
        if(  scalar(@tokens) < scalar( @names) )
        {

            #print STDERR "warning $file:$lineno: tokens=", scalar(@tokens), " names=", scalar(@names), "\n$line\n";
            next;
            utils::stacktrace();

            die $line;
        }
        my %data;
        for(my $i=0; $i < scalar(@names); $i++ )
        {
            $data{$names[$i]} = $tokens[$i];
            #print $names[$i], "=",  $tokens[$i], "\n";
        }
        $data {'line'} = $line;
        push @records, \%data;
        #exit(0);
    }
    $h->close();
    return @records;
}




#
#
# to
# subject
# html
# text
# images
sub send_email( @ )
{

    my (%argv) = @_;

    my $boundary = "FILEBOUNDARY";
    my $boundary_tag = "--";

    my $to      = $argv{'to'};
    my $subject = $argv{'subject'};
    my $html    = $argv{'html'};
    my $text    = $argv{'text'};
    my $images  = $argv{'images'};



    my $f = new IO::File( "| /usr/lib/sendmail -t");
    print $f "To: $to\n";
    print $f "Subject: $subject\n";
    print $f "Content-Type: multipart/mixed; boundary=\"$boundary\"\n";


    if(defined($html))
    {
        print $f $boundary_tag, $boundary, "\n";
        print $f "Content-Type: text/html\n";
        print $f "Content-Disposition: inline\n\n";
        print $f $html, "\n";
    }
    if(defined($text))
    {
        print $f $boundary_tag, $boundary, "\n";
        print $f "Content-Type: text/plain\n";
        print $f "Content-Disposition: inline\n\n";
        print $f $text, "\n";
    }
    if( defined($images ))
    {
        foreach my $i (@{$images})
        {
            print $f $boundary_tag, $boundary, "\n";
            print $f "Content-Type: image/png\n";
            print $f "Content-Disposition: inline; filename=", utils::filename($i), "\n";
            print $f "Content-Transfer-Encoding: base64\n\n";

            print STDERR "image = ", utils::filename($i), "\n";
            my $io = new IO::File("$i") or die "$!";
            my $buf;
            while (read($io, $buf, 60*57)) {
                print $f encode_base64($buf);
            }
            $io->close();
            #last;
        }
        print $f $boundary_tag, $boundary, $boundary_tag;
    }
    $f->close();
}


# option relative data, in days
sub get_today_relative($)
{
    my ($relative) = @_;
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime(time);
    if( defined($relative))
    {
        print STDERR "check relative $relative\n";
        my $yesterday_midday=timelocal(0,0,12,$mday,$mon,$year) + $relative*24*60*60;
        ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($yesterday_midday);
    }
    return ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst);
}

sub get_today_str($)
{
    my ($relative) = @_;
    my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =get_today_relative($relative);
    $year += 1900;
    $mon += 1;
    $date = sprintf("%04d%02d%02d", $year, $mon, $mday );
    #print STDERR "$date \n";
    return $date;
}
return 1;
