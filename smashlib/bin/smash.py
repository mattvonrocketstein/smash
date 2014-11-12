#!/usr/bin/env python
#

import os, sys
from smashlib.util import require_ipy
from smashlib.python import ope

REQUIRE_VERSION = '3.0'
require_ipy(REQUIRE_VERSION)

def main():
    from smashlib import embed
    from smashlib.util.ipy import SmashConfig, SmashUserConfig
    smash_prof = SmashConfig.ensure()
    user_conf = SmashUserConfig.ensure()
    embed(["--profile-dir={0}".format(smash_prof),])

entry = main

if __name__=='__main__':
    main()
