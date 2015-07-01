""" smashlib.patches
"""
from smashlib.patches.cd import PatchCDMagic
from smashlib.patches.pushd import PatchPushdMagic
__all__ = [
    PatchCDMagic.__name__,
    PatchPushdMagic.__name__,
]
