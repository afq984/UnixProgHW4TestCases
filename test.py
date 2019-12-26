import os
import urllib.parse
import requests
import lxml.html
import pytest
import random
from conftest import BASE_URL, LOCAL_DIR


def url_for(path):
    return urllib.parse.urljoin(BASE_URL, path)


def randstr():
    return random.getrandbits(32).to_bytes(4, 'little')


def get(path, params=None):
    if params is None:
        params = {
            randstr(): randstr(),
            randstr(): randstr(),
            randstr(): randstr(),
        }
    return requests.get(url_for(path), params=params, allow_redirects=False)


def post(path, data):
    return requests.post(url_for(path), data=data, allow_redirects=False)


DIR2_FILES = [
    'audio.ogg',
    'image.png',
    'plain.txt',
    'simple.html',
    'video.mp4',
]

ROOT_FILES = [
    '01-super-mario-bros.ogg',
    'audio.ogg',
    'big_buck_bunny_720p_1mb.mp4',
    'dir1',
    'dir2',
    'image.png',
    'noperm',
    'pikachu.png',
    'plain.txt',
    'post.php',
    'printenv.php',
    'printenv_php.txt',
    'printenv.sh',
    'printenv_sh.txt',
    'simple.html',
    'video.mp4',
    'xdir1',
    'xdir2',
]

STATIC_PATHS = [
    *DIR2_FILES,
    'printenv_php.txt',
    'printenv_sh.txt',
    'dir1/index.html',
    *[f'dir2/{name}' for name in DIR2_FILES],
]


@pytest.fixture(scope='module', autouse=True)
def sanitize():
    try:
        requests.get(BASE_URL)
    except requests.ConnectionError:
        pytest.exit('cannot connect to --base-url, aborting early')


@pytest.mark.parametrize('path', STATIC_PATHS)
def test_GET_static(path):
    """
    If a requested object can be found, your server has to return "200 OK"
    status as well as the proper headers and content for the browser to render
    the document correctly.
    """
    resp = get(path)
    assert resp.status_code == 200
    with open(os.path.join(LOCAL_DIR, path), 'rb') as file:
        assert resp.content == file.read()


NOT_FOUND = [
    '...',
    'GG',
    'dir2/index.html',
    'dir3',
]


@pytest.mark.parametrize('path', NOT_FOUND)
def test_GET_does_not_exist(path):
    """
    If a requested object does not exist, your server has to return a
    "403 FORBIDDEN" status and provide error messages.
    """
    resp = get(path)
    assert resp.status_code == 403


@pytest.mark.parametrize('path', ['noperm'])
def test_GET_inaccessible(path):
    """
    If a requested object is inaccessible, your server has to return a
    "404 NOT FOUND" status and provide error messages.
    """
    resp = get(path)
    assert resp.status_code == 404


@pytest.mark.parametrize('path', ['dir1', 'dir2', 'xdir1', 'xdir2'])
def test_GET_dir_301(path):
    """
    If a requested object is a directory, your program have to check whether
    the requested directory has a slash (/) at the end of the URL.
    """
    resp = get(path)
    assert resp.status_code == 301
    assert urllib.parse.urlparse(
        urllib.parse.urljoin(
            resp.url, resp.headers['Location'])).path == urllib.parse.urlparse(
                url_for(path + '/')).path


def test_GET_dir_index():
    """
    If there is a readable index.html file, you can simply send the content of
    index.html back to the browser.
    """
    resp = get('dir1/')
    assert resp.status_code == 200
    with open(os.path.join(LOCAL_DIR, 'dir1/index.html'), 'rb') as file:
        assert resp.content == file.read()


def test_GET_dir_index_inaccessible():
    """
    If there is a index.html file, but it is not readable, you can simply send
    "403 FORBIDDEN" status to the browser.
    """
    resp = get('xdir1/')
    assert resp.status_code == 403


LIST_DIRS = [('dir2/', DIR2_FILES), ('/', ROOT_FILES)]


@pytest.mark.parametrize('path,files', LIST_DIRS)
def test_GET_dir_listing(path, files):
    """
    If there is not a readable index.html file,
    but the directory is readable, you have to list the files and directories
    found in the requested directory.
    The list can be in either a plain-text document or a html document.
    """
    resp = get(path)
    assert resp.status_code == 200
    for filename in files:
        assert filename in resp.text


@pytest.mark.parametrize('path,files', LIST_DIRS)
def test_GET_dir_listing_extra(path, files):
    """
    It would be a plus if your response is a html document with hyperlinks
    point to the location of files and directories in the requested directory.
    """
    resp = get(path)
    assert resp.status_code == 200
    html = lxml.html.fromstring(resp.content)
    html.make_links_absolute(urllib.parse.urlparse(url_for('dir2/')).path)
    hrefs = [href.rstrip('/') for href in html.xpath('//a/@href')]
    for filename in files:
        assert urllib.parse.urlparse(urllib.parse.urljoin(
            resp.url, filename)).path in hrefs


def test_GET_dir_no_index_not_readable():
    """
    If there is not a readable index.html file, and the directory is not
    readable, you have to send "404 NOT FOUND" status to the browser.
    """
    resp = get('xdir2/')
    assert resp.status_code == 404


@pytest.mark.parametrize('path', ['printenv.php', 'printenv.sh'])
def test_GET_cgi_REQUEST_METHOD(path):
    """
    Implement CGI execution using GET requests: Environment variable -
    REQUEST_METHOD=GET
    """
    resp = get(path, params={'p': 'hello world', 'q': '中文測試'})
    assert resp.status_code == 200
    assert 'REQUEST_METHOD=GET' in resp.text


@pytest.mark.parametrize('path', ['printenv.php', 'printenv.sh'])
def test_GET_cgi_QUERY_STRING(path):
    """
    If a question mark (?) is used in the URL, add the content after (?) into a
    environment variable QUERY_STRING.
    """
    qs = urllib.parse.urlencode({'p': 'hello world', 'q': '中文測試'})
    resp = get(path + '?' + qs)
    assert resp.status_code == 200
    assert f'QUERY_STRING={qs}' in resp.text


def test_POST_cgi_REQUEST_METHOD():
    """
    Implement CGI execution using POST requests: Environment variable -
    REQUEST_METHOD=POST.
    """
    resp = post('post.php', data='hello world :)')
    assert resp.status_code == 200
    assert 'REQUEST_METHOD=POST' in resp.text


def test_POST_cgi_body():
    """
    You will also have to setup a pipe to forward inputs from the browser to
    the CGI script.
    """
    resp = post('post.php', data='hello world :)')
    assert resp.status_code == 200
    assert 'hello world :)' in resp.text


def test_POST_cgi_query_string():
    resp = post('post.php?hello_WORLD', data='not empty')
    assert resp.status_code == 200
    assert 'REQUEST_METHOD=POST' in resp.text
    assert 'hello_WORLD' in resp.text


def test_POST_cgi_empty_body():
    resp = post('post.php?hello_WORLD', data='')
    assert resp.status_code == 200
    assert 'REQUEST_METHOD=POST' in resp.text
    assert 'hello_WORLD' in resp.text
