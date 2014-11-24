#!/usr/bin/env bash
#
set -ex
SMASH_HOME="$HOME/.smash"
GOT_SMASH_REPO=0
SMASH_INST_REQ="$SMASH_HOME/install_requirements.txt"
SMASH_INST_PROG="$SMASH_HOME/install.py"
ORIGIN="`git remote show -n origin 2>/dev/null| grep Fetch | cut -d: -f2-`"
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
        git clone https://github.com/mattvonrocketstein/smash.git ~/.smash
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
echo
echo "Installation complete.  Run it with ~/bin/smash"
