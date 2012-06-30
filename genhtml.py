#/usr/bin/python
#coding=utf8

import ast
import os
import string
import subprocess
import urllib


def get_movie_list(folder):
    folders = subprocess.check_output(['ls', folder])
    return folders.split('\n')[:-1]


def imdbapi(movie):
    url = 'http://www.imdbapi.com/?t=%s' % movie
    return ast.literal_eval(urllib.urlopen(url).read())


def get_cover(movie, url):
    return urllib.urlretrieve(url, movie.replace('/', ':') + '.jpg')


def generate_html(movies):
    lines = []
    errors = []
    for movie in movies:
        data = imdbapi(movie)
        try:
            title = data['Title']
            id = data['imdbID']
            if data['Poster'] != 'N/A':
                if os.path.isfile(title.replace('/', ':')):
                    get_cover(title, data['Poster'])
            else:
                errors.append(('cover error', movie))
        except KeyError:
            title = movie
            id = raw_input('Enter an id for %s: ' % title)
            errors.append(('data error', movie))
        print 'Working ... %s' % title
        url = 'http://imdb.com/title/%s' % id
        line = '<a href="%s" target="_blank">%s</a><br>' % (url, title)
        lines.append(line)
        if title == 'American History X':
            print 'Am his'
            src = title + '.jpg'
            line = '<img border="0" src="%s" height="317"><br>' % src
        else:
            src = title.replace('/', ':') + '.jpg'
            line = '<img border="0" src="%s" height="317"><br>' % src
        lines.append(line)
    print errors
    return '\n'.join(lines)


def main():
    # NOTE For images to work they must not contain ":" in the name and
    # permissions may have to be set with the command:
    # chcon -R -v -t httpd_sys_rw_content_t file.jpg
    # TODO Fix code so that it only downloads data and images when required,
    # and fix exceptions, such as those of City of God and American History X.
    # NOTE Useful command: sed -i 's/to_replace/to_replace_with/g' filename
    start = ['<!DOCTYPE html>', '<html>', '<body>'] 
    a = ['<center><p><em>a:</em></p>']
    a.append(generate_html(get_movie_list('/run/media/haukur/a/movies')))
    b = ['<p><em>b:</em></p>']
    b.append(generate_html(get_movie_list('/run/media/haukur/b/movies')))
    end = ['</center></body>', '</html>']
    with open('/var/www/html/index.html', 'w') as index:
        index.write('\n'.join(start + a + b + end))


if __name__ == '__main__':
    main()
