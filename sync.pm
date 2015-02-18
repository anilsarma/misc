package sync;
use utils;
use color;
use Log;
;

my $logger = new Log();

#usate s=source file, d=destination file
sub sync_file( $$ )
{
    my ( $s, $d ) = @_;

    my $dest = utils::dirname( $d );

    #my $d = "$dest/$f"; $d =~ s/\/\//\//g;
    #my $s = "$src/$f";  $s =~ s/\/\//\//g;

    my $cp = 0;
    #print "DEBUG:(sync_file) checking $src/$f $dest/$f \n";
    if( ! -f "$s" )
    {
        $logger->log( color::red("\tWarning: $s not found") . "\n" );
        $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
        return ;
    }
    if ( -f "$d" )
    {
        my $ssum = utils::checksum( "$s" );
        my $dsum = utils::checksum( "$d" );
        if( $ssum ne $dsum )
        {
            #print color::red("\tcheck sum different ($ssum) ($dsum)"). "\n";
            $cp = 1;
        }
    }
    else
    {
        $cp = 1;
    }

    if( $cp == 1 )
    {
        #print "copy ".color::blue("$s" ). " => ". color::red("$d");
        $logger->log("copy ".color::blue("$s" ). " => ". color::red("$d") ."\n");
        system "mkdir -p $dest " if ( ! -d $dest );

        if( ! -d "$dest" )
        {
            $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
            $logger->log( color::red("sync: cannot create directory $dest") . "\n" );
            sync::close();
            exit(-1);
        }
        #system "/bin/cp -f '$s' '$d'";
        system "rsync  -vvart '$s' '$d' 2>&1 > /dev/null";


        die "failed to copy $s $d " if ( !-f "$d" && !-l "$d"  );
        #$log->log "\n";
    }
}
sub copy_dir_contents( $$ );
sub copy_dir_contents( $$ )
{
    my ($srcdir, $destdir) = @_;

    opendir CDIR, "$srcdir";
    my @c = readdir CDIR;
    closedir CDIR;

    my @dirs;
    my @files;
    foreach my $f( @c )
    {
        next if ( $f =~ /^\.+$/);
        push @dirs, "$f" if (-d "$srcdir/$f");
        #print "dir $srcdir/$f\n";
        if (-f "$srcdir/$f")
        {
            #print STDERR "copy $srcdir/$f, $destdir/$f\n";
            sync_file( "$srcdir/$f", "$destdir/$f" )
        }
    }
    foreach my $d(@dirs)
    {
        copy_dir_contents( "$srcdir/$d", "$destdir/$d");
    }
}

# directory or file.
sub sync( $$ )
{
    my ($src, $dest) = @_;

    if( -f $src )
    {
        # source is a file

        if( -f $dest )
        {
            sync_file( $src, $dest);
        }
        elsif (-d $dest || $dest =~ /\/$/ ) #terminates with a directory seprator
        {
            my $srcfile = utils::filename( $src );
            #die "copy $src ". $dest. "/". $srcfile
            sync_file( $src, $dest. "/". $srcfile );
        }
        else
        {
            # we reach here assume that the destination is a file
            sync_file( $src, $dest);
        }
    }
    elsif( -d "$src" )
    {
        if ( -f "$dest" )
        {
            $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
            $logger->log(color::red("error: source $src is a directory and destination $dest is a file" )."\n");
            sync::close();
            exit(-1);
        }
        copy_dir_contents( $src, $dest );

    }
}

sub rsync_pipe( $ )
{
    my ($mcmd ) = @_;
    open PIPE,  $mcmd;
    my $last = "";
    my $retcode = 0;
    my $enabled  =0;
    while ( my $line =<PIPE>)
    {
        chomp $line;
        if( $line =~ /rsync error:/ )
        {
            $logger->log(color::red("$line" ) ."\n");
            $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
            sync::close();
            exit(-1);
        }
        if( $enabled == 0 && $line =~ /delta-transmission/ )
        {
            $enabled = 1;
            next;
        }
        next if( $line =~ /speedup is/ );
        next if( $line =~ /bytes\/sec/ );
        next if( $line =~ /total:/ );
        next if ($enabled == 0);
        next if ( $line =~ /\/$/);
        if ( $line !~ /is uptodate$/)
        {
            $logger->log("copy ".color::blue("$src/$line" ). " => ". color::red("$dest/$line") ."\n");
        }

    }
    close PIPE;
}
sub fast_sync_file ($$)
{
    my ($src, $dest) = @_;
    my $mcmd = "rsync  -vvartc  $src $dest 2>&1|";
    my $dir = utils::dirname $dest;
    if( !-d "$dir" )
    {
        system "mkdir -p $dir";
    }
    open PIPE,  $mcmd;
    my $last = "";
    my $retcode = 0;
    my $enabled  =0;
    while ( my $line =<PIPE>)
    {
        chomp $line;
        if( $line =~ /rsync error:/ )
        {
            $logger->log(color::red("$line" ) ."\n");
            $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
            sync::close();
            exit(-1);
        }
        if( $line =~ /rsync/ )
        {
            $logger->log(color::green("$line" ) ."\n");
        }
        if( $enabled == 0 && $line =~ /delta-transmission/ )
        {
            $enabled = 1;
            next;
        }
        next if( $line =~ /speedup is/ );
        next if( $line =~ /bytes\/sec/ );
        next if( $line =~ /total:/ );
        next if ($enabled == 0);
        next if ( $line =~ /\/$/);
        next if( length($line) == 0 );
        if ( $line !~ /is uptodate$/)
        {
            $logger->log("copy ".color::blue("$src/$line" ). " => ". color::red("$dest/$line") ."\n");
        }

    }
    close PIPE;
}

sub fast_sync ($$)
{
    my ($src, $dest) = @_;
    my $mcmd = "rsync  -vvart  $src $dest 2>&1 |";

    open PIPE,  $mcmd;
    my $last = "";
    my $retcode = 0;
    my $enabled  =0;
    while ( my $line =<PIPE>)
    {
        chomp $line;
        if( $line =~ /rsync error:/ )
        {
            $logger->log(color::red("$line" ) ."\n");
            $logger->log(color::blue(utils::stacktrace_print() ) ."\n");
            sync::close();
            exit(-1);
        }
        if( $line =~ /rsync/ )
        {
            $logger->log(color::green("$line" ) ."\n");
        }
        if( $enabled == 0 && $line =~ /delta-transmission/ )
        {
            $enabled = 1;
            next;
        }
        next if( $line =~ /speedup is/ );
        next if( $line =~ /bytes\/sec/ );
        next if( $line =~ /total:/ );
        next if ($enabled == 0);
        next if ( $line =~ /\/$/);
        next if( length($line) == 0 );
        if ( $line !~ /is uptodate$/)
        {
            $logger->log("copy ".color::blue("$src/$line" ). " => ". color::red("$dest/$line") ."\n");
        }

    }
    close PIPE;
}
sub close()
{
    $logger->close();
}


1;
