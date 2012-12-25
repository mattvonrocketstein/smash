""" host completion for SmaSh.

    this doesn't work with many programs right now,
    but, if something is missing just add an extra
    re to the HOST_REGEXES list.
"""
from smashlib.util import report, set_complete
from smashlib.smash_plugin import SmashPlugin

HOST_REGEXES = [
    'ssh .*$',
    'ssh .*@$', ]

URL_REGEXES = [
    '.*http://.*$',
    '.*https://.*$', ]

def get_hosts():
    from smashlib.python import ope, opj
    hosts = []
    hosts_file = '/etc/hosts'
    if ope(hosts_file):
        with open(hosts_file) as fhandle:
            for line in fhandle.readlines():
                line = line.strip()
                if line.startswith('#'):
                    continue
                for host in line.split()[1:]:
                    if all(['::' not in host,
                            'ip6-' not in host]):
                        hosts.append(host.strip())
    return hosts

def uri_completer(self, event):
    """ uri's are treated a bit differently
        (evidently ipython's internals split on `:`)
    """
    return ['//'+h for h in get_hosts()]

def host_completer(self, event):
    return get_hosts()

class Plugin(SmashPlugin):
    def install(self):
        for regex in HOST_REGEXES:
            set_complete(host_completer, regex)
        for regex in URL_REGEXES:
            set_complete(uri_completer, regex)
