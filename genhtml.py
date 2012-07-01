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
    url = 'http://www.imdbapi.com/?t=%s' % movie
    return ast.literal_eval(urllib.urlopen(url).read())


def get_cover(movie, url):
    '''Download and return the cover for the movie from url.'''
    return urllib.urlretrieve(url, movie.replace('/', ':') + '.jpg')


def fix_name(filename):
    '''Fix filenames so that the files can be used.'''
    #filename = filename.replace(' -', ':')
    special = ' -+,.!'
    allowed = string.lowercase + string.uppercase + string.digits + special
    return ''.join([char for char in filename if char in allowed])


def generate_html(movies):
    '''Generate html code that lists movies and information about them.'''
    # TODO Clean and restructure - this function should only generate and
    # return html code, not retrieve it.
    # Also generate a fiew plaintext files.
    # Restructure code so that anyone can use it to create a html file for
    # themselves.
    # XXX Use the folder name for the movie name in the HTML.
    # TODO Do not scan existing titles.
    lines = []
    errors = []
    for movie in movies:
        data = imdbapi(movie)
        try:
            title = fix_name(data['Title'])
            jpg = title
            id = data['imdbID']
            if data['Poster'] != 'N/A':
                if not os.path.isfile(jpg):
                    get_cover(jpg, data['Poster'])
            else:
                errors.append(('cover error', movie))
        except KeyError:
            title = movie
            id = raw_input('Enter an id for %s: ' % title)
            errors.append(('data error', movie))
        print 'Working ... %s' % movie
        url = 'http://imdb.com/title/%s' % id
        # TODO Make the image a link and remove the link above it?
        src = jpg + '.jpg'
        line = '<a href="%s" target="_blank"><img src="%s" ' % (url, src)
        line += 'border="0" height="470" width="317"></a>'
        lines.append(line)
    if errors:
        print errors
    return '\n'.join(lines)


def plaintext():
    '''Generate a plaintext list over the films in the two drives.'''
    with open('/var/www/html/listi', 'w') as listi:
        movies = size_list('/run/media/haukur/a/movies/')
        listi.write('Drive a (%i G):\n' % movies[1])
        for size, movie in movies[0]:
            listi.write('%s\t%s\n' % (size, movie))
        movies = size_list('/run/media/haukur/b/movies/')
        listi.write('Drive b (%i G):\n' % movies[1])
        for size, movie in movies[0]:
            listi.write('%s\t%s\n' % (size, movie))


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
    a.append(generate_html(get_movie_list('/run/media/haukur/a/movies')))
    b = ['<p><h1>Kvikmyndir <em>b</em></h1></p>']
    b.append(generate_html(get_movie_list('/run/media/haukur/b/movies')))
    c = ['<br><br><p>Kvikmyndum er raðað eftir staðsetningu og svo eftir '
         + 'stafrófsröð.<br>Með því að smella á mynd má komast inn á IMDb '
         + 'síðu viðkomandi myndar.</p><p><a href="http://hph.no-ip.org/listi"'
         + '>Listi</a> á textaformi.</p>']
    end = ['</center>', '</body>', '</html>']
    # NOTE A temporary file for testing purposes can easily be specified here.
    with open('/var/www/html/index.html', 'w') as index:
        index.write('\n'.join(start + a + b + c + end))
    plaintext()


if __name__ == '__main__':
    main()
