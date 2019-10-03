#! /usr/bin/perl -w

use DBI;
use strict;
use File::Copy;
use Config::Simple;

# read in the database config
my $cfg;
if( -r $ENV{"HOME"} . "/centos-ml.cfg" ) {
        $cfg = new Config::Simple($ENV{"HOME"} . "/centos-ml.cfg");
} elsif( -r "/etc/mirmon/centos-ml.cfg" ) {
        $cfg = new Config::Simple("/etc/mirmon/centos-ml.cfg");
} else {
        die("Can't read centos-ml.cfg");
}

my $driver = "mysql";
my $host="localhost";
my $database = $cfg->param('database');
my $dbhost = $cfg->param('dbhost');
my $user = $cfg->param('dbuser');
my $password = $cfg->param('dbpass');

my $dsn ="DBI:$driver:database=$database;host=$host";

my $dbh = DBI->connect($dsn, $user, $password)
     || die "Cannot connect to database Error: $!";


open(CEN, ">/tmp/centoslist2") || die "Unable to open temp list file";

my $sth = $dbh->prepare("SELECT cc,http,ftp FROM mirrors WHERE `status` = 'Master'");

my $rec;

if ( !$sth )
    { die "Error:" . $dbh->errstr . "\n"; }
if ( !$sth->execute )
    { die "Error:" . $sth->errstr ."\n"; }
my $cc;

while($rec = $sth->fetchrow_hashref())
        {
	$cc =$rec->{"cc"};
	if (!$cc){$cc = "us"; };
 
        print CEN $cc." ".$rec->{"http"}."\n";
        }

$sth->finish();

$dbh->disconnect();

close CEN;

move("/tmp/centoslist2","/var/lib/centos-mirrors/mirmon_centoslist");


