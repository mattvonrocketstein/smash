#!/usr/bin/env python
#
import os

from smashlib.import_hooks import hijack_ipython_module


def main():
    os.environ['SMASH'] = '1'
    hijack_ipython_module()
    # imports below must come after hijack
    from smashlib import embed
    from smashlib.config import SmashConfig, SmashUserConfig
    smash_prof = SmashConfig.ensure()['profile']
    SmashUserConfig.ensure()
    embed(["--profile-dir={0}".format(smash_prof), ],
          # do not let smash inspect the caller context
          # and automatically update globals/locals
          user_ns=None
          )

entry = main

if __name__ == '__main__':
    main()
