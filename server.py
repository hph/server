#/usr/bin/python
#coding=utf8

import os
import sys
from subprocess import Popen, PIPE
from time import sleep
from urllib import urlopen


def users_and_IPs():
    '''Get the users connected via the SSH daemon and their IPs. Requires sudo
    privileges.'''
    # The command is "netstat -nutp | grep sshd".
    p1 = Popen(['netstat', '-nutp'], stdout=PIPE)
    p2 = Popen(['grep', 'sshd'], stdin=p1.stdout, stdout=PIPE)
    output = p2.communicate()[0]
    if not output:
        return
    output = output[:-1].split('\n')
    output = [out.split() for out in output]
    if len(output) > 0:
        output = [(out[7], out[4].split(':')[0]) for out in output]
    # Remove duplicate user-IP tuples.
    return sorted(set(output))


def active_files(directory='/media/', user=False):
    '''Find which files are active (being downloaded or uploaded) and by
    who. Requires sudo privileges.'''
    # The command is "lsof -w | grep $directory [| grep $user]".
    p1 = Popen(['lsof', '-w'], stdout=PIPE)
    p2 = Popen(['grep', directory], stdin=p1.stdout, stdout=PIPE)
    if user:
        p3 = Popen(['grep', user], stdin=p2.stdout, stdout=PIPE)
        output = p3.communicate()[0]
    else:
        output = p2.communicate()[0]
    if not output:
        return
    output = output[:-1].split('\n')
    split_output = [out.split() for out in output]
    users = [out[2] for out in split_output]
    files = [out.split('/media')[1] for out in output]
    # Ugly but necessary to remove PIDs (they're numbers) from the user list.
    for _ in xrange(len(users) * 2):
        for i, user in enumerate(users):
            if user.isdigit():
                users.remove(user)
                # Necessary to zip the correct users and files together.
                files.pop(i)
    return zip(users, files)


def get_country_from_IP(IP):
    '''Return the country of the IP.'''
    try:
        # API available at "https://github.com/appliedsec/pygeoip".
        # Also requires "GeoAPI.dat" to be in the same folder as server.py,
        # available at: "http://www.maxmind.com/app/geolite". 
        # This API claims to be 99.5% accurate.
        from pygeoip import GeoIP

        gi = pygeoip.GeoIP('GeoIP.dat', pygeoip.MEMORY_CACHE)
        return gi.country_code_by_addr(str(IP))
    except:
        # This API is not completely accurate but allows for manual corrections
        # at their website.
        site = 'http://api.hostip.info/country.php?ip='
        return urlopen(site + str(IP)).read()


def get_size():
    '''Get the size of the terminal window.'''
    # XXX Temporary hack - do it with subprocess instead.
    # Also, doesn't work with the "watch" program (the program, not the
    # function) which makes it useless.
    rows, columns = os.popen('stty size > /dev/null', 'r').read().split()
    return int(rows), int(columns)


def watch(term_width):
    '''Temporary function to print a list of users, their IPs and users and
    active files.'''
    to_print = []
    alarms = []
    allowed = ['ek', 'ej', 'dev', 'shp', 'gj', 'sths', 'jas', 'gks', 'thth',
               'jat', 'zhp', 'hi']
    IPs = []
    countries = {}
    users = users_and_IPs()
    if users:
        max_len = max([len(user[0]) for user in users])
        title = 'Users:  '
        while len(title) < max_len + 2:
            title += ' '
        to_print.append('%sIP addresses:' % title)
        title_len = len(title)
        for user in users:
            if user[0] not in allowed or user[1] not in IPs:
                if user[1] not in IPs:
                    IPs.append(user[1])
                try:
                    IP = get_country_from_IP(user[1])
                except:
                    IP = ''
                country = get_country(IP)
                countries[IP] = country
                alarms.append((user[0], user[1], countries[IP]))
            to_print.append('%s%s' % (user[0].ljust(title_len),
                            user[1] + ' (%s)' % countries[IP]))
    active = active_files()
    if active:
        max_len = max([len(user[0]) for user in active])
        if users:
            title = '\nUsers:  '
        else:
            title = 'Users:   '
        while len(title) < max_len + 2:
            title += ' '
        to_print.append('%sActive files:' % title)
        title_len = len(title[1:])
        if not users:
            title_len += 1
        for file in active:
            to_print.append('%s%s' % (file[0].ljust(title_len), file[1]))
    spl = lambda a, b: [a[i:i + b] for i in xrange(0, len(a), b)]
    for line in to_print:
        line = spl(line, term_width)
        if line[0]:
            print line[0]
        else:
            print '\n'
        if len(line) > 1:
            for line in line[1:]:
                print title_len * ' ' + line
    if alarms:
        print '\nALARMS:'
        for alarm in alarms:
            print 'User "%s" (%s) does not exist!' % (alarm[0], alarm[2])


def get_country(country_code):
    '''Scan countrycodes.txt and return a list of countries and country
    codes.'''
    countrycodes = {}
    with open('countrycodes.txt', 'r') as file:
        for line in file:
            data = line.split()
            code = data[-3]
            country = ' '.join(data[:-3]).title()
            countrycodes[code] = country
    try:
        return countrycodes[country_code]
    except:
        return None


def authenticate():
    '''Prompt the user for the superuser password if required.'''
    # The euid (effective user id) of the superuser is 0.
    euid = os.geteuid()
    if euid != 0:
        args = ['sudo', sys.executable] + sys.argv[:] + [os.environ]
        # Replaces the current running process with the sudo authentication.
        os.execlpe('sudo', *args)
    return True


def log():
    '''Read /var/log/secure for ssh logs.'''
    pass


def main():
    # The program requires sudo privileges. Pass a custom terminal width as an
    # argument if it is not 80. You can also run this program with the UNIX
    # program "watch", i.e. "sudo watch python server.py".
    authenticate()
    if len(sys.argv) > 1:
        term_width = sys.argv[1]
    else:
        term_width = 80
    watch(term_width)


if __name__ == '__main__':
    main()
