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
SMASH_ALREADY_CLONED=0
SMASH_INST_REQ="$SMASH_HOME/install_requirements.txt"
SMASH_INST_PROG="$SMASH_HOME/install.py"
ORIGIN="`git remote show -n origin 2>/dev/null| grep Fetch | cut -d: -f2-`"
if [ -z "$SMASH_BRANCH" ]; then BRANCH=master; else BRANCH=$SMASH_BRANCH; fi;
if [ -z $1 ]; then BRANCH=$BRANCH; else BRANCH=$1; fi;
echo "using branch: $BRANCH"
if [ ! -z "$ORIGIN" -a "$ORIGIN" != " " ]; then
    BNAME="`basename $ORIGIN`";
    if [ $BNAME = "smash.git" ]; then
        SMASH_INST_REQ="`pwd`/install_requirements.txt";
        SMASH_INST_PROG="`pwd`/install.py";
        SMASH_ALREADY_CLONED=1;
    fi
fi
echo "using install_requirements: $SMASH_INST_REQ"


if [ ! -d "$SMASH_HOME" ]; then
    echo "$SMASH_HOME does not exist";
    if [ $SMASH_ALREADY_CLONED = 0 ]; then
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
    CREATED_SMASH_VENV=1;
else
    echo "$SMASH_HOME is already a virtualenv, will not create a new one";
    CREATED_SMASH_VENV=0
fi

cd $SMASH_HOME
CURRENT_BRANCH=`git rev-parse HEAD`
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    git checkout $BRANCH
    git pull
fi

$SMASH_HOME/bin/pip install -r $SMASH_INST_REQ
$SMASH_HOME/bin/python $SMASH_INST_PROG
set +x
echo
echo -e "\x1B[31mSummary\x1B[0m"
echo "  SMASH_HOME = $SMASH_HOME"
echo "  SMASH_ALREADY_CLONED = $SMASH_ALREADY_CLONED"
echo "  BRANCH = $BRANCH, $CURRENT_BRANCH"
echo "  CREATED_SMASH_VENV = $CREATED_SMASH_VENV"
echo
echo -e "\x1B[31mInstallation complete.  Run it with ~/bin/smash\x1B[0m"
