#!/usr/bin/env bash
#
# This bootstraps smash, eventually running smash's install.py and setup.py
# Why not just run setup.py directly?  Smash should be installed in a private
# virtual environment (not shared between users).  This venv needs to be setup,
# and before install.py can actually be used, install_requirements.txt must be
# installed.
#
# The bootstrap command accepts a single argument, which is the smash branch to
# use.  If the argument is not given, it defaults to master.  Alternatively, you
# can set the SMASH_BRANCH environment variable, for instance if you're invoking
# this bootstrap with curl:
#
#  $ bootstrap=https://raw.githubusercontent.com/mattvonrocketstein/smash/master/bootstrap.sh
#  $ SMASH_BRANCH=master curl bootstrap|bash
#
set -ex
SMASH_HOME="$HOME/.smash"
GOT_SMASH_REPO=0
SMASH_INST_REQ="$SMASH_HOME/install_requirements.txt"
SMASH_INST_PROG="$SMASH_HOME/install.py"
BRANCH=
ORIGIN="`git remote show -n origin 2>/dev/null| grep Fetch | cut -d: -f2-`"
if [ -z "$SMASH_BRANCH" ]; then BRANCH=master; else BRANCH=$SMASH_BRANCH; fi;
if [ -z $1 ]; then BRANCH=$BRANCH; else BRANCH=$1; fi;
echo "using branch: $BRANCH"
if [ ! -z "$ORIGIN" -a "$ORIGIN" != " " ]; then
    BNAME="`basename $ORIGIN`";
    if [ $BNAME = "smash.git" ]; then
        SMASH_INST_REQ="`pwd`/install_requirements.txt";
        SMASH_INST_PROG="`pwd`/install.py";
        GOT_SMASH_REPO=1;
    fi
fi
echo "using install_requirements: $SMASH_INST_REQ"


if [ ! -d "$SMASH_HOME" ]; then
    echo "$SMASH_HOME does not exist";
    if [ $GOT_SMASH_REPO = 0 ]; then
        echo "You need smash code.  Cloning it to $SMASH_HOME";
        git clone --branch=$BRANCH https://github.com/mattvonrocketstein/smash.git ~/.smash
    else
        echo "Already have smash code, will not clone"
        echo "Creating dir $SMASH_HOME";
        mkdir $SMASH_HOME
    fi
else
    echo "$SMASH_HOME exists already..";
fi

if [ ! -d "$SMASH_HOME/bin" ]; then
    echo "$SMASH_HOME is not a virtualenv yet.  Creating it..";
    virtualenv --no-site-packages $SMASH_HOME;

else
    echo "$SMASH_HOME is already a virtualenv, will not create a new one"
fi

$SMASH_HOME/bin/pip install -r $SMASH_INST_REQ
$SMASH_HOME/bin/python $SMASH_INST_PROG
echo
echo "Summary: "
echo "SMASH_HOME = $SMASH_HOME"
echo "GOT_SMASH_REPO = $GOT_SMASH_REPO"
echo "BRANCH = $BRANCH"
echo
echo "Installation complete.  Run it with ~/bin/smash"
