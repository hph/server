#/usr/bin/python
#coding=utf8

from os import popen
from subprocess import Popen, PIPE
from time import sleep


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


def active_files(directory='/run/media/', user=False):
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
    files = [out.split('/run/media/haukur')[1] for out in output]
    # Ugly but necessary to remove PIDs (they're numbers) from the user list.
    for _ in xrange(len(users) * 2):
        for i, user in enumerate(users):
            if user.isdigit():
                users.remove(user)
                # Necessary to zip the correct users and files together.
                files.pop(i)
    return zip(users, files)


def watch():
    '''Watch for connections and list active files.'''
    while True:
        print 'Active users:'
        users = users_and_IPs()
        if users:
            for user, ip in users:
                print '%s (%s)' % user, ip
        active = active_files()
        if active:
            for user, file in active:
                print '%s -- %s' % user, file
        sleep(1)


def get_size():
    '''Get the size of the terminal window.'''
    # XXX Temporary hack - do it with subprocess instead.
    # Also, doesn't work with the "watch" program (the program, not the
    # function) which makes it useless.
    rows, columns = popen('stty size > /dev/null', 'r').read().split()
    return int(rows), int(columns)


def watch(term_width=80):
    '''Temporary function to print a list of users, their IPs and users and
    active files.'''
    to_print = []
    users = users_and_IPs()
    if users:
        max_len = max([len(user[0]) for user in users])
        title = 'Users:  '
        while len(title) < max_len + 2:
            title += ' '
        to_print.append('%sIP addresses:' % title)
        title_len = len(title)
        for user in users:
            to_print.append('%s%s' % (user[0].ljust(title_len), user[1]))
    active = active_files()
    if active:
        max_len = max([len(user[0]) for user in active])
        title = '\nUsers:  '
        while len(title) < max_len + 2:
            title += ' '
        to_print.append('%sActive files:' % title)
        title_len = len(title[1:])
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


def log():
    '''Read /var/log/secure for ssh logs.'''
    pass


def main():
    watch()


if __name__ == '__main__':
    main()
