# coding: utf-8
"""Test the contents webservice API."""

import base64
import io
import json
import os
import shutil
from unicodedata import normalize

pjoin = os.path.join

import requests

from IPython.html.utils import url_path_join, url_escape
from IPython.html.tests.launchnotebook import NotebookTestBase, assert_http_error
from IPython.nbformat import read, write, from_dict
from IPython.nbformat.v4 import (
    new_notebook, new_markdown_cell,
)
from IPython.nbformat import v2
from IPython.utils import py3compat
from IPython.utils.data import uniq_stable


def notebooks_only(dir_model):
    return [nb for nb in dir_model['content'] if nb['type']=='notebook']

def dirs_only(dir_model):
    return [x for x in dir_model['content'] if x['type']=='directory']


class API(object):
    """Wrapper for contents API calls."""
    def __init__(self, base_url):
        self.base_url = base_url

    def _req(self, verb, path, body=None, params=None):
        response = requests.request(verb,
                url_path_join(self.base_url, 'api/contents', path),
                data=body, params=params,
        )
        response.raise_for_status()
        return response

    def list(self, path='/'):
        return self._req('GET', path)

    def read(self, path, type_=None, format=None):
        params = {}
        if type_ is not None:
            params['type'] = type_
        if format is not None:
            params['format'] = format
        return self._req('GET', path, params=params)

    def create_untitled(self, path='/', ext='.ipynb'):
        body = None
        if ext:
            body = json.dumps({'ext': ext})
        return self._req('POST', path, body)

    def mkdir_untitled(self, path='/'):
        return self._req('POST', path, json.dumps({'type': 'directory'}))

    def copy(self, copy_from, path='/'):
        body = json.dumps({'copy_from':copy_from})
        return self._req('POST', path, body)

    def create(self, path='/'):
        return self._req('PUT', path)

    def upload(self, path, body):
        return self._req('PUT', path, body)

    def mkdir_untitled(self, path='/'):
        return self._req('POST', path, json.dumps({'type': 'directory'}))

    def mkdir(self, path='/'):
        return self._req('PUT', path, json.dumps({'type': 'directory'}))

    def copy_put(self, copy_from, path='/'):
        body = json.dumps({'copy_from':copy_from})
        return self._req('PUT', path, body)

    def save(self, path, body):
        return self._req('PUT', path, body)

    def delete(self, path='/'):
        return self._req('DELETE', path)

    def rename(self, path, new_path):
        body = json.dumps({'path': new_path})
        return self._req('PATCH', path, body)

    def get_checkpoints(self,  path):
        return self._req('GET', url_path_join(path, 'checkpoints'))

    def new_checkpoint(self,  path):
        return self._req('POST', url_path_join(path, 'checkpoints'))

    def restore_checkpoint(self, path, checkpoint_id):
        return self._req('POST', url_path_join(path, 'checkpoints', checkpoint_id))

    def delete_checkpoint(self, path, checkpoint_id):
        return self._req('DELETE', url_path_join(path, 'checkpoints', checkpoint_id))

class APITest(NotebookTestBase):
    """Test the kernels web service API"""
    dirs_nbs = [('', 'inroot'),
                ('Directory with spaces in', 'inspace'),
                (u'unicodé', 'innonascii'),
                ('foo', 'a'),
                ('foo', 'b'),
                ('foo', 'name with spaces'),
                ('foo', u'unicodé'),
                ('foo/bar', 'baz'),
                ('ordering', 'A'),
                ('ordering', 'b'),
                ('ordering', 'C'),
                (u'å b', u'ç d'),
               ]
    hidden_dirs = ['.hidden', '__pycache__']

    dirs = uniq_stable([py3compat.cast_unicode(d) for (d,n) in dirs_nbs])
    del dirs[0]  # remove ''
    top_level_dirs = {normalize('NFC', d.split('/')[0]) for d in dirs}

    @staticmethod
    def _blob_for_name(name):
        return name.encode('utf-8') + b'\xFF'

    @staticmethod
    def _txt_for_name(name):
        return u'%s text file' % name

    def setUp(self):
        nbdir = self.notebook_dir.name
        self.blob = os.urandom(100)
        self.b64_blob = base64.encodestring(self.blob).decode('ascii')

        for d in (self.dirs + self.hidden_dirs):
            d.replace('/', os.sep)
            if not os.path.isdir(pjoin(nbdir, d)):
                os.mkdir(pjoin(nbdir, d))

        for d, name in self.dirs_nbs:
            d = d.replace('/', os.sep)
            # create a notebook
            with io.open(pjoin(nbdir, d, '%s.ipynb' % name), 'w',
                         encoding='utf-8') as f:
                nb = new_notebook()
                write(nb, f, version=4)

            # create a text file
            with io.open(pjoin(nbdir, d, '%s.txt' % name), 'w',
                         encoding='utf-8') as f:
                f.write(self._txt_for_name(name))

            # create a binary file
            with io.open(pjoin(nbdir, d, '%s.blob' % name), 'wb') as f:
                f.write(self._blob_for_name(name))

        self.api = API(self.base_url())

    def tearDown(self):
        nbdir = self.notebook_dir.name

        for dname in (list(self.top_level_dirs) + self.hidden_dirs):
            shutil.rmtree(pjoin(nbdir, dname), ignore_errors=True)

        if os.path.isfile(pjoin(nbdir, 'inroot.ipynb')):
            os.unlink(pjoin(nbdir, 'inroot.ipynb'))

    def test_list_notebooks(self):
        nbs = notebooks_only(self.api.list().json())
        self.assertEqual(len(nbs), 1)
        self.assertEqual(nbs[0]['name'], 'inroot.ipynb')

        nbs = notebooks_only(self.api.list('/Directory with spaces in/').json())
        self.assertEqual(len(nbs), 1)
        self.assertEqual(nbs[0]['name'], 'inspace.ipynb')

        nbs = notebooks_only(self.api.list(u'/unicodé/').json())
        self.assertEqual(len(nbs), 1)
        self.assertEqual(nbs[0]['name'], 'innonascii.ipynb')
        self.assertEqual(nbs[0]['path'], u'unicodé/innonascii.ipynb')

        nbs = notebooks_only(self.api.list('/foo/bar/').json())
        self.assertEqual(len(nbs), 1)
        self.assertEqual(nbs[0]['name'], 'baz.ipynb')
        self.assertEqual(nbs[0]['path'], 'foo/bar/baz.ipynb')

        nbs = notebooks_only(self.api.list('foo').json())
        self.assertEqual(len(nbs), 4)
        nbnames = { normalize('NFC', n['name']) for n in nbs }
        expected = [ u'a.ipynb', u'b.ipynb', u'name with spaces.ipynb', u'unicodé.ipynb']
        expected = { normalize('NFC', name) for name in expected }
        self.assertEqual(nbnames, expected)

        nbs = notebooks_only(self.api.list('ordering').json())
        nbnames = [n['name'] for n in nbs]
        expected = ['A.ipynb', 'b.ipynb', 'C.ipynb']
        self.assertEqual(nbnames, expected)

    def test_list_dirs(self):
        print(self.api.list().json())
        dirs = dirs_only(self.api.list().json())
        dir_names = {normalize('NFC', d['name']) for d in dirs}
        print(dir_names)
        print(self.top_level_dirs)
        self.assertEqual(dir_names, self.top_level_dirs)  # Excluding hidden dirs

    def test_list_nonexistant_dir(self):
        with assert_http_error(404):
            self.api.list('nonexistant')

    def test_get_nb_contents(self):
        for d, name in self.dirs_nbs:
            path = url_path_join(d, name + '.ipynb')
            nb = self.api.read(path).json()
            self.assertEqual(nb['name'], u'%s.ipynb' % name)
            self.assertEqual(nb['path'], path)
            self.assertEqual(nb['type'], 'notebook')
            self.assertIn('content', nb)
            self.assertEqual(nb['format'], 'json')
            self.assertIn('content', nb)
            self.assertIn('metadata', nb['content'])
            self.assertIsInstance(nb['content']['metadata'], dict)

    def test_get_contents_no_such_file(self):
        # Name that doesn't exist - should be a 404
        with assert_http_error(404):
            self.api.read('foo/q.ipynb')

    def test_get_text_file_contents(self):
        for d, name in self.dirs_nbs:
            path = url_path_join(d, name + '.txt')
            model = self.api.read(path).json()
            self.assertEqual(model['name'], u'%s.txt' % name)
            self.assertEqual(model['path'], path)
            self.assertIn('content', model)
            self.assertEqual(model['format'], 'text')
            self.assertEqual(model['type'], 'file')
            self.assertEqual(model['content'], self._txt_for_name(name))

        # Name that doesn't exist - should be a 404
        with assert_http_error(404):
            self.api.read('foo/q.txt')

        # Specifying format=text should fail on a non-UTF-8 file
        with assert_http_error(400):
            self.api.read('foo/bar/baz.blob', type_='file', format='text')

    def test_get_binary_file_contents(self):
        for d, name in self.dirs_nbs:
            path = url_path_join(d, name + '.blob')
            model = self.api.read(path).json()
            self.assertEqual(model['name'], u'%s.blob' % name)
            self.assertEqual(model['path'], path)
            self.assertIn('content', model)
            self.assertEqual(model['format'], 'base64')
            self.assertEqual(model['type'], 'file')
            b64_data = base64.encodestring(self._blob_for_name(name)).decode('ascii')
            self.assertEqual(model['content'], b64_data)

        # Name that doesn't exist - should be a 404
        with assert_http_error(404):
            self.api.read('foo/q.txt')

    def test_get_bad_type(self):
        with assert_http_error(400):
            self.api.read(u'unicodé', type_='file')  # this is a directory

        with assert_http_error(400):
            self.api.read(u'unicodé/innonascii.ipynb', type_='directory')

    def _check_created(self, resp, path, type='notebook'):
        self.assertEqual(resp.status_code, 201)
        location_header = py3compat.str_to_unicode(resp.headers['Location'])
        self.assertEqual(location_header, url_escape(url_path_join(u'/api/contents', path)))
        rjson = resp.json()
        self.assertEqual(rjson['name'], path.rsplit('/', 1)[-1])
        self.assertEqual(rjson['path'], path)
        self.assertEqual(rjson['type'], type)
        isright = os.path.isdir if type == 'directory' else os.path.isfile
        assert isright(pjoin(
            self.notebook_dir.name,
            path.replace('/', os.sep),
        ))

    def test_create_untitled(self):
        resp = self.api.create_untitled(path=u'å b')
        self._check_created(resp, u'å b/Untitled.ipynb')

        # Second time
        resp = self.api.create_untitled(path=u'å b')
        self._check_created(resp, u'å b/Untitled1.ipynb')

        # And two directories down
        resp = self.api.create_untitled(path='foo/bar')
        self._check_created(resp, 'foo/bar/Untitled.ipynb')

    def test_create_untitled_txt(self):
        resp = self.api.create_untitled(path='foo/bar', ext='.txt')
        self._check_created(resp, 'foo/bar/untitled.txt', type='file')

        resp = self.api.read(path='foo/bar/untitled.txt')
        model = resp.json()
        self.assertEqual(model['type'], 'file')
        self.assertEqual(model['format'], 'text')
        self.assertEqual(model['content'], '')

    def test_upload(self):
        nb = new_notebook()
        nbmodel = {'content': nb, 'type': 'notebook'}
        path = u'å b/Upload tést.ipynb'
        resp = self.api.upload(path, body=json.dumps(nbmodel))
        self._check_created(resp, path)

    def test_mkdir_untitled(self):
        resp = self.api.mkdir_untitled(path=u'å b')
        self._check_created(resp, u'å b/Untitled Folder', type='directory')

        # Second time
        resp = self.api.mkdir_untitled(path=u'å b')
        self._check_created(resp, u'å b/Untitled Folder 1', type='directory')

        # And two directories down
        resp = self.api.mkdir_untitled(path='foo/bar')
        self._check_created(resp, 'foo/bar/Untitled Folder', type='directory')

    def test_mkdir(self):
        path = u'å b/New ∂ir'
        resp = self.api.mkdir(path)
        self._check_created(resp, path, type='directory')

    def test_mkdir_hidden_400(self):
        with assert_http_error(400):
            resp = self.api.mkdir(u'å b/.hidden')

    def test_upload_txt(self):
        body = u'ünicode téxt'
        model = {
            'content' : body,
            'format'  : 'text',
            'type'    : 'file',
        }
        path = u'å b/Upload tést.txt'
        resp = self.api.upload(path, body=json.dumps(model))

        # check roundtrip
        resp = self.api.read(path)
        model = resp.json()
        self.assertEqual(model['type'], 'file')
        self.assertEqual(model['format'], 'text')
        self.assertEqual(model['content'], body)

    def test_upload_b64(self):
        body = b'\xFFblob'
        b64body = base64.encodestring(body).decode('ascii')
        model = {
            'content' : b64body,
            'format'  : 'base64',
            'type'    : 'file',
        }
        path = u'å b/Upload tést.blob'
        resp = self.api.upload(path, body=json.dumps(model))

        # check roundtrip
        resp = self.api.read(path)
        model = resp.json()
        self.assertEqual(model['type'], 'file')
        self.assertEqual(model['path'], path)
        self.assertEqual(model['format'], 'base64')
        decoded = base64.decodestring(model['content'].encode('ascii'))
        self.assertEqual(decoded, body)

    def test_upload_v2(self):
        nb = v2.new_notebook()
        ws = v2.new_worksheet()
        nb.worksheets.append(ws)
        ws.cells.append(v2.new_code_cell(input='print("hi")'))
        nbmodel = {'content': nb, 'type': 'notebook'}
        path = u'å b/Upload tést.ipynb'
        resp = self.api.upload(path, body=json.dumps(nbmodel))
        self._check_created(resp, path)
        resp = self.api.read(path)
        data = resp.json()
        self.assertEqual(data['content']['nbformat'], 4)

    def test_copy(self):
        resp = self.api.copy(u'å b/ç d.ipynb', u'å b')
        self._check_created(resp, u'å b/ç d-Copy1.ipynb')
        
        resp = self.api.copy(u'å b/ç d.ipynb', u'å b')
        self._check_created(resp, u'å b/ç d-Copy2.ipynb')
    
    def test_copy_copy(self):
        resp = self.api.copy(u'å b/ç d.ipynb', u'å b')
        self._check_created(resp, u'å b/ç d-Copy1.ipynb')
        
        resp = self.api.copy(u'å b/ç d-Copy1.ipynb', u'å b')
        self._check_created(resp, u'å b/ç d-Copy2.ipynb')
    
    def test_copy_path(self):
        resp = self.api.copy(u'foo/a.ipynb', u'å b')
        self._check_created(resp, u'å b/a.ipynb')
        
        resp = self.api.copy(u'foo/a.ipynb', u'å b')
        self._check_created(resp, u'å b/a-Copy1.ipynb')

    def test_copy_put_400(self):
        with assert_http_error(400):
            resp = self.api.copy_put(u'å b/ç d.ipynb', u'å b/cøpy.ipynb')

    def test_copy_dir_400(self):
        # can't copy directories
        with assert_http_error(400):
            resp = self.api.copy(u'å b', u'foo')

    def test_delete(self):
        for d, name in self.dirs_nbs:
            print('%r, %r' % (d, name))
            resp = self.api.delete(url_path_join(d, name + '.ipynb'))
            self.assertEqual(resp.status_code, 204)

        for d in self.dirs + ['/']:
            nbs = notebooks_only(self.api.list(d).json())
            print('------')
            print(d)
            print(nbs)
            self.assertEqual(nbs, [])

    def test_delete_dirs(self):
        # depth-first delete everything, so we don't try to delete empty directories
        for name in sorted(self.dirs + ['/'], key=len, reverse=True):
            listing = self.api.list(name).json()['content']
            for model in listing:
                self.api.delete(model['path'])
        listing = self.api.list('/').json()['content']
        self.assertEqual(listing, [])

    def test_delete_non_empty_dir(self):
        """delete non-empty dir raises 400"""
        with assert_http_error(400):
            self.api.delete(u'å b')

    def test_rename(self):
        resp = self.api.rename('foo/a.ipynb', 'foo/z.ipynb')
        self.assertEqual(resp.headers['Location'].split('/')[-1], 'z.ipynb')
        self.assertEqual(resp.json()['name'], 'z.ipynb')
        self.assertEqual(resp.json()['path'], 'foo/z.ipynb')
        assert os.path.isfile(pjoin(self.notebook_dir.name, 'foo', 'z.ipynb'))

        nbs = notebooks_only(self.api.list('foo').json())
        nbnames = set(n['name'] for n in nbs)
        self.assertIn('z.ipynb', nbnames)
        self.assertNotIn('a.ipynb', nbnames)

    def test_rename_existing(self):
        with assert_http_error(409):
            self.api.rename('foo/a.ipynb', 'foo/b.ipynb')

    def test_save(self):
        resp = self.api.read('foo/a.ipynb')
        nbcontent = json.loads(resp.text)['content']
        nb = from_dict(nbcontent)
        nb.cells.append(new_markdown_cell(u'Created by test ³'))

        nbmodel= {'content': nb, 'type': 'notebook'}
        resp = self.api.save('foo/a.ipynb', body=json.dumps(nbmodel))

        nbfile = pjoin(self.notebook_dir.name, 'foo', 'a.ipynb')
        with io.open(nbfile, 'r', encoding='utf-8') as f:
            newnb = read(f, as_version=4)
        self.assertEqual(newnb.cells[0].source,
                         u'Created by test ³')
        nbcontent = self.api.read('foo/a.ipynb').json()['content']
        newnb = from_dict(nbcontent)
        self.assertEqual(newnb.cells[0].source,
                         u'Created by test ³')


    def test_checkpoints(self):
        resp = self.api.read('foo/a.ipynb')
        r = self.api.new_checkpoint('foo/a.ipynb')
        self.assertEqual(r.status_code, 201)
        cp1 = r.json()
        self.assertEqual(set(cp1), {'id', 'last_modified'})
        self.assertEqual(r.headers['Location'].split('/')[-1], cp1['id'])

        # Modify it
        nbcontent = json.loads(resp.text)['content']
        nb = from_dict(nbcontent)
        hcell = new_markdown_cell('Created by test')
        nb.cells.append(hcell)
        # Save
        nbmodel= {'content': nb, 'type': 'notebook'}
        resp = self.api.save('foo/a.ipynb', body=json.dumps(nbmodel))

        # List checkpoints
        cps = self.api.get_checkpoints('foo/a.ipynb').json()
        self.assertEqual(cps, [cp1])

        nbcontent = self.api.read('foo/a.ipynb').json()['content']
        nb = from_dict(nbcontent)
        self.assertEqual(nb.cells[0].source, 'Created by test')

        # Restore cp1
        r = self.api.restore_checkpoint('foo/a.ipynb', cp1['id'])
        self.assertEqual(r.status_code, 204)
        nbcontent = self.api.read('foo/a.ipynb').json()['content']
        nb = from_dict(nbcontent)
        self.assertEqual(nb.cells, [])

        # Delete cp1
        r = self.api.delete_checkpoint('foo/a.ipynb', cp1['id'])
        self.assertEqual(r.status_code, 204)
        cps = self.api.get_checkpoints('foo/a.ipynb').json()
        self.assertEqual(cps, [])
