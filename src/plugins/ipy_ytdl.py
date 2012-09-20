""" ipy_ytdl
    shortcuts for youtube download
"""
import os

CMD = '{bin} --max-quality=18 --format=18/22/37/38/83/82/85/84 "{url}"'
#cmd = '{bin} --max-quality=6 "{url}"'

def ytdl(url):
    """ """
    if not url.startswith('http://'):
        if url.startswith('www'): url = 'http://' + url
        else:
            assert len(url)==11,'expected an id or url.. got '+url
            url = 'http://www.youtube.com/watch?v=' + url
    _bin = os.popen('which youtube-dl').read().strip()
    assert os.path.exists(_bin), "youtube-dl not found"
    cmd = CMD.format(bin=_bin, url=url)
    print '>>>',cmd
    return os.system(cmd)

from smash.plugins import SmashPlugin
class Plugin(SmashPlugin):
    def install(self):
        __IPYTHON__.user_ns.update(ytdl=ytdl)
