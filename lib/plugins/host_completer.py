""" host completion for SmaSh.

    Should always work when typing urls or emails, but other
    than that you'll have to be using one of the known programs
    (see HOST_REGEXES for a list).
"""
import smashlib
from smashlib.python import ope, opj
from smashlib.util import report, set_complete
from smashlib.smash_plugin import SmashPlugin

# This doesn't work with many programs right now, but, if something
# is missing just add an extra re to the HOST_REGEXES list.
HOST_REGEXES = [
    'wget .*$',
    'ssh .*@$', 'ssh .*$',
    'mosh .*@$', 'mosh .*$',
    ]

URL_REGEXES = [
    '.*http://.*$',
    '.*https://.*$', ]

def get_hosts():
    hosts, hosts_file = [], '/etc/hosts'
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
    hosts_json = opj(smashlib._meta['config_dir'],'hosts.json')
    if ope(hosts_json):
        with open(hosts_json) as fhandle:
            hosts_json = demjson.decode(fhandle.read())
        for alias,host in hosts_json.items():
            hosts += [alias,host]
    return hosts

def uri_completer(self, event):
    """ uri's are treated a bit differently because
        evidently ipython's internals split on `:` """
    return [ '//' + h for h in get_hosts() ]

def host_completer(self, event):
    return get_hosts()

class Plugin(SmashPlugin):
    def install(self):
        for regex in HOST_REGEXES:
            set_complete(host_completer, regex)
        for regex in URL_REGEXES:
            set_complete(uri_completer, regex)
