from io import BytesIO
import sys
import codecs
import mimetypes
import random
import string

from .compat import compat_cookiejar, compat_pickle


class ClientCookieJar(compat_cookiejar.CookieJar):
    """Custom CookieJar that can be pickled to/from strings
    """
    def __init__(self, cookie_string=None, policy=None):
        compat_cookiejar.CookieJar.__init__(self, policy)
        if cookie_string:
            if isinstance(cookie_string, bytes):
                self._cookies = compat_pickle.loads(cookie_string)
            else:
                self._cookies = compat_pickle.loads(cookie_string.encode('utf-8'))

    @property
    def auth_expires(self):
        try:
            return min([
                cookie.expires for cookie in self
                if cookie.name in ('sessionid', 'ds_user_id', 'ds_user')
                and cookie.expires])
        except ValueError:
            # empty sequence
            pass
        return None

    @property
    def expires_earliest(self):
        """For backward compatibility"""
        return self.auth_expires

    def dump(self):
        return compat_pickle.dumps(self._cookies)


class MultipartFormDataEncoder(object):
    """
    Modified from
    http://stackoverflow.com/questions/1270518/python-standard-library-to-post-multipart-form-data-encoded-data
    """
    def __init__(self, boundary=None):
        self.boundary = boundary or \
            ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(30))
        self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, fields, files):
        """
        :param fields: sequence of (name, value) elements for regular form fields
        :param files: sequence of (name, filename, contenttype, filedata) elements for data to be uploaded as files
        :return:
        """
        encoder = codecs.getencoder('utf-8')
        for (key, value) in fields:
            key = self.u(key)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder('\r\n')
            if isinstance(value, (int, float)):
                value = str(value)
            yield encoder(self.u(value))
            yield encoder('\r\n')
        for (key, filename, contenttype, fd) in files:
            key = self.u(key)
            filename = self.u(filename)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('Content-Type: {}\r\n'.format(
                contenttype or mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            yield encoder('Content-Transfer-Encoding: binary\r\n')
            yield encoder('\r\n')
            yield (fd, len(fd))
            yield encoder('\r\n')
        yield encoder('--{}--\r\n'.format(self.boundary))

    def encode(self, fields, files):
        body = BytesIO()
        for chunk, _ in self.iter(fields, files):
            body.write(chunk)
        return self.content_type, body.getvalue()
