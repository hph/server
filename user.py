#/usr/bin/python
#coding=utf8

import argparse
import os
import sys


def authenticate():
    '''Prompt the user for the superuser password if required.'''
    # The euid (effective user id) of the superuser is 0.
    euid = os.geteuid()
    if euid != 0:
        args = ['sudo', sys.executable] + sys.argv[:] + [os.environ]
        # Replaces the current running process with the sudo authentication.
        os.execlpe('sudo', *args)
    return True


def create_user(user):
    '''Creates the user, passwords, sets rules and restarts the SSH daemon.'''
    authenticate()
    calls = [('useradd -G sshers %s' % user,
              'create a new user (%s).' % user),
             ('passwd %s' % user,
              'set a SSH password for %s.' % user),
             ('htpasswd /var/www/passwd/passwords %s' % user,
              'set a HTTP password for %s.' % user),
             ('echo "AllowUsers %s" >> /etc/ssh/sshd_config' % user,
              'set new rule to allow %s to connect via SSH or SFTP.' % user),
             ('service sshd restart',
              'restart the SSH daemon'),
             ('service httpd restart',
              'restart the HTTP daemon')]
    for call, info in calls:
        print 'Attempting to %s' % info
        if not os.system(call):
            print 'Success! [%s]\n' % info[:-1]


def delete_user(user):
    '''Delete a user and remove all data.'''
    authenticate()
    calls = [('userdel %s' % user,
              'delete a user (%s).' % user),
             ('rm -rf /home/%s' % user,
              'delete the %s\'s home directory.' % user),
             ('service sshd restart',
              'restart the SSH daemon'),
             ('service httpd restart',
              'restart the HTTP daemon')]
    for call, info in calls:
        print 'Attempting to %s' % info
        if not os.system(call):
            print 'Success! [%s]\n' % info[:-1]
    print 'You must manually do the following:'
    print 'Remove %s\'s password from /var/www/passwd/passwords.' % user
    print 'Remove AllowUsers %s rule from /etc/ssh/sshd_config.' % user


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--create', metavar='USER', default=False,
                        help='''Create a new user.''')
    parser.add_argument('-d', '--delete', metavar='USER', default=False,
                        help='''Delete a user.''')
    args = parser.parse_args()
    if args.create:
        create_user(args.create)
    elif args.delete:
        delete_user(args.delete)


if __name__ == '__main__':
    main()
