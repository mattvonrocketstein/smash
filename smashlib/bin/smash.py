#!/usr/bin/env python
#

import os
from smashlib.util import require_ipy


def main():
    REQUIRE_VERSION = '3.0'
    require_ipy(REQUIRE_VERSION)
    os.environ['SMASH'] = '1'
    from smashlib import embed
    from smashlib.config import SmashConfig, SmashUserConfig
    smash_prof = SmashConfig.ensure()['profile']
    SmashUserConfig.ensure()
    embed(["--profile-dir={0}".format(smash_prof),])

entry = main

if __name__=='__main__':
    main()
