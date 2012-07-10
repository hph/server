#/usr/bin/python
#coding=utf8

import ast
import os
import string
import subprocess
import urllib


def get_movie_list(folder):
    '''List the folders in folder.'''
    folders = subprocess.check_output(['ls', folder])
    return folders.split('\n')[:-1]


def size_list(path):
    '''List the items in a folder, using du.'''
    items = subprocess.check_output('du -sh %s*' % path, shell=True)
    items = items.split('\n')[:-1]
    movies = []
    for item in items:
        size_file = item.split('\t')
        size_file[1] = size_file[1].split('/')
        movies.append((size_file[0], size_file[1][-1]))
    total_size = 0
    for size, _ in movies:
        if size[-1] == 'M':
            total_size += float(size[:-1]) * 0.001
        else:
            total_size += float(size[:-1])
    return movies, int(total_size)


def imdbapi(movie):
    '''Download the available data at imdbapi.com.'''
    print 'Downloading the IMDb data of %s.' % movie
    url = 'http://www.imdbapi.com/?t=%s' % movie
    return ast.literal_eval(urllib.urlopen(url).read())


def get_cover(movie, url):
    '''Download and return the cover for the movie from url.'''
    print 'Downloading the cover of %s.' % movie
    return urllib.urlretrieve(url, movie.replace('/', ':') + '.jpg')


def fix_name(filename):
    '''Fix filenames so that the files can be used.'''
    #filename = filename.replace(' -', ':')
    special = ' -+,.!'
    allowed = string.lowercase + string.uppercase + string.digits + special
    return ''.join([char for char in filename if char in allowed])


def fix_errors():
    '''Fix known errors.'''
    path = '/var/www/backup/'
    subprocess.call('cp %s*.jpg .' % path, shell=True)


def save_data(data, filename='/var/www/data'):
    '''Save data from imdbapi.'''
    try:
        title = data['Title']
        ID = data['imdbID']
        poster = data['Poster']
        data = (title, ID, poster)
        with open(filename, 'a') as file:
            file.write('%s\t%s\t%s\n' % (title, ID, poster))
    except (KeyError, TypeError) as error:
        # Do something? Example: City of God. See lines 116-124.
        return
    return data


def get_data(movie, filename='/var/www/data'):
    '''Get the movie url if it exists.'''
    data = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.split('\t')
            data.append(tuple(line))
    for item in data:
        if item[0] == movie:
            return item


def generate_html(movies):
    '''Generate html code that lists movies and information about them.'''
    lines = []
    errors = []
    for movie in movies:
        data = get_data(movie)
        if not data:
            data = imdbapi(movie)
            data = save_data(data)
        if data:
            title = fix_name(data[0])
            # Get a different cover name for the Redux version.
            if movie == 'Apocalypse Now Redux':
                title = movie
            jpg = title
            id = data[1]
            try:
                if not os.path.isfile('/var/www/html/%s.jpg' % jpg):
                    get_cover(jpg, data[2])
            except:
                errors.append(('cover error', movie))
        # Unnecessary else clause? Doesn't really matter, remove later if so.
        else:
            title = movie
            jpg = title
            # For some reason the imdbapi find this film.
            if title == 'City of God':
                id = 'tt0317248'
            elif title == 'The Conversation':
                id = 'tt0071360'
            else:
                id = raw_input('Enter an id for %s: ' % title)
                errors.append(('data error', movie))
        url = 'http://imdb.com/title/%s' % id
        # TODO Make the image a link and remove the link above it?
        src = jpg + '.jpg'
        line = '<a href="%s" target="_blank"><img src="%s" ' % (url, src)
        line += 'border="0" height="211" width="143"></a>'
        lines.append(line)
    if errors:
        print 'Error(s):'
        for error in errors:
            print '%s: %s' % (error[0], error[1])
    return '\n'.join(lines)


def plaintext():
    '''Generate a plaintext lists over the films in the two drives.'''
    with open('/var/www/html/movies', 'w') as listi:
        movies = size_list('/media/a/movies/')
        listi.write('Drive a (%i G):\n' % movies[1])
        for size, movie in movies[0]:
            listi.write('%s\t%s\n' % (size, movie))
        movies = size_list('/media/b/movies/')
        listi.write('Drive b (%i G):\n' % movies[1])
        for size, movie in movies[0]:
            listi.write('%s\t%s\n' % (size, movie))
    with open('/var/www/html/newest', 'w') as newest:
        folders = subprocess.check_output(['ls', '-t',
                                           '/media/a/movies'])
        newest.write(folders)
    with open('/var/www/html/soon', 'w') as soon:
        path = '/media/a/temp/'
        folders = subprocess.check_output('du -sh %s*' % path, shell=True)
        soon.write(folders)


def main():
    # NOTE For images to work they must not contain ":" in the name and
    # permissions may have to be set with the command:
    # chcon -R -v -t httpd_sys_rw_content_t file.jpg
    # Another useful command (search and replace): 
    # sed -i 's/search/replace/g' filename
    # TODO Fix code so that it only downloads data and images when required,
    # and fix exceptions, such as those of City of God and American History X.
    # TODO Add more information from imdbapi AND local, such as filesize,
    # subtitles available, resolution, etc.
    # TODO Add "expected soon" section from temp downloads folder.
    start = ['<!DOCTYPE html>', '<html>', '<body>', '<center>']
    a = ['<p><h1>Kvikmyndir <em>a</em></h1></p>']
    a.append(generate_html(get_movie_list('/media/a/movies')))
    b = ['<p><h1>Kvikmyndir <em>b</em></h1></p>']
    b.append(generate_html(get_movie_list('/media/b/movies')))
    c = ['<br><br><p>Kvikmyndum er raðað eftir staðsetningu og svo eftir '
         + 'stafrófsröð.<br>Með því að smella á mynd má komast inn á IMDb '
         + 'síðu viðkomandi myndar.</p>'
         + '<p><a href="http://hph.no-ip.org/movies">Kvikmynda-</a>, <a '
         + 'href="http://hph.no-ip.org/music">tónlistar-</a> og <a '
         + 'href="http://hph.no-ip.org/books">bókalisti</a> á textaformi.</p>'
         + '<p> <a href="http://hph.no-ip.org/newest">Nýjustu</a> '
         + 'kvikmyndirnar og <a href="http://hph.no-ip.org/soon">væntanlegar'
         + '</a> kvikmyndir.</p>']
    end = ['</center>', '</body>', '</html>']
    # NOTE A temporary file for testing purposes can easily be specified here.
    with open('/var/www/html/index.html', 'w') as index:
        print 'Generating HTML file.'
        index.write('\n'.join(start + a + b + c + end))
    fix_errors()
    plaintext()


if __name__ == '__main__':
    main()
