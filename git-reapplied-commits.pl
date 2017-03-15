#!/usr/bin/perl -w
#
# Prints details of commits to the new branch more than once since the common
# base commit with the old branch

use Getopt::Std;
use Env;
use File::Basename;
use File::stat;

$sc_name              = basename("$0");
$usage                = "usage: $sc_name -o <branch-1> -n <branch-2>\n";

getopts('o:n:') or die "$usage";


die "$usage" if (!$opt_o);
die "$usage" if (!$opt_n);
$branch_1 = "$opt_o";
$branch_2 = "$opt_n";
my $base_commit = `git merge-base $branch_1 $branch_2`;
chomp $base_commit;
my @commits = `git log --decorate --pretty='format: %h (committer:%cn %cI) [%an %aI] %s' --abbrev-commit $base_commit..$branch_2`;

my %commit_stuff;
foreach my $commit_line (@commits) {
    $key = $commit_line;
    $key =~ s/^.*\[/\[/;
    @line_cache = ();
    if (defined $commit_stuff{$key}) {
        @line_cache = @{ $commit_stuff{$key} };
    }
    push (@line_cache, $commit_line);
    @{ $commit_stuff{$key} } = @line_cache;
}
for my $key (keys %commit_stuff) {
    @line_cache = @{ $commit_stuff{$key} };
    my $size = $#line_cache + 1;
    if (1 lt scalar(@line_cache)) {
        foreach my $line (@line_cache) {
            print $line;
        }
    }
}
exit 0;
