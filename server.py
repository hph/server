#/usr/bin/python
#coding=utf8

from subprocess import Popen, PIPE


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


def logs():
    '''Read /var/log/secure for ssh logs.'''
    pass


def main():
    # For testing the output of the functions.
    print 'Checking for connected users and their IPs.'
    print users_and_IPs()
    print 'Checking for active files (downloads, uploads).'
    print active_files()


if __name__ == '__main__':
    main()
