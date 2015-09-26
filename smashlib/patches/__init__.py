""" smashlib.patches
"""
from smashlib.patches.base import Patch
from smashlib.patches.cd import PatchCDMagic
from smashlib.patches.pushd import PatchPushdMagic
__all__ = [
    Patch.__name__,
    PatchCDMagic.__name__,
    PatchPushdMagic.__name__,
]
