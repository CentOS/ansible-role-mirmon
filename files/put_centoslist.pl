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

my $state;
my $sth;
my $query;

my $dsn ="DBI:$driver:database=$database;host=$host";

my $dbh = DBI->connect($dsn, $user, $password)
     || die "Cannot connect to database Error: $!";

my $behind = 28*60*60;
my $ood = 52*60*60;

#print "behind $behind ood $ood\n";


open(CEN, "</var/lib/centos-mirrors/mirmonlist.state") || die "Unable to open centos list file";

while (<CEN>)
	{

	$state = "";

#	print $_;
	my ($url, $age, $last, $last_success, $probehist, $statehist, $lastprobe) = split (" ",$_);
#	print "$url - $last\n";
	if($age eq "undef")
		{
		$state = "timeout";
		}
	my $states= $statehist;

#print "$url $states";

#	$states =~ s/.*-//;

my $field;

if ($url =~ "^ftp")
	{
	$field = "ftp";
	}
else
	{
	$field = "http";
	}		

if(!$state)
{

my $agediff = $lastprobe - $age;

print "diff $agediff\n";

if ($agediff > $ood)
	{
	$state = "out of date";
	}
elsif ($agediff > $behind)
	{
	$state = "behind";
	}
elsif ($agediff <= $behind)
	{
	$state = "current";
	}
}
	
# $states = substr($states, length($states) -1);

#	if ($states eq "s")
#		{
#		$state = "current";
#		}
#	elsif ($states eq "b")
#		{
#		$state = "behind";
#		}
#	elsif ($states eq "f")
#		{
#		$state = "out of date";
#		}
#	
#	print "states $states - $state\n";
#
#	
	$query = "UPDATE `mirrors` SET `state` = \'$state\' WHERE `$field` = \'$url\';\n";
 	print $query;

	$sth = $dbh->prepare( "UPDATE `mirrors` SET `state` = '$state' WHERE `$field` = '$url';");
	
	if ( !$sth )
    		{ die "Error:" . $dbh->errstr . "\n"; }
	if ( !$sth->execute )
		{ die "Error:" . $sth->errstr ."\n"; }
	$sth->finish();
	
	}


exit;

$dbh->disconnect();

close CEN;



