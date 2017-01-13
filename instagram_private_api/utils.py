import time
import hmac
import base64
import hashlib
from random import randint


def gen_user_breadcrumb(size):
    key = 'iN4$aGr0m'
    dt = int(time.time() * 1000)

    # typing time elapsed
    time_elapsed = randint(500, 1500) + size * randint(500, 1500)

    text_change_event_count = max(1, size / randint(3, 5))

    data = '%(size)s %(elapsed)s %(count)s %(dt)s' % {
        'size': size, 'elapsed': time_elapsed, 'count': text_change_event_count, 'dt': dt
    }
    return '%s\n%s\n' % (
        base64.b64encode(hmac.new(key.encode('ascii'), data.encode('ascii'), digestmod=hashlib.sha256).digest()),
        base64.b64encode(data))


class Chunk(object):
    def __init__(self, index, start, end, total):
        self.index = index
        self.start = start
        self.end = end
        self.total = total

    @property
    def is_first(self):
        return self.index == 0

    @property
    def is_last(self):
        return self.index == self.total - 1

    @property
    def length(self):
        return self.end - self.start


def chunk_generator(chunk_count, chunk_size, file_data):
    total_len = len(file_data)
    for i in range(chunk_count):
        start_range = i * chunk_size
        end_range = (start_range + chunk_size) if i < (chunk_count - 1) else total_len
        chunk_info = Chunk(i, start_range, end_range, chunk_count)
        yield chunk_info, file_data[chunk_info.start: chunk_info.end]


def max_chunk_size_generator(chunk_size, file_data):
    chunk_count, final_chunk = divmod(len(file_data), chunk_size)
    if final_chunk:
        chunk_count += 1
    return chunk_generator(chunk_count, chunk_size, file_data)


def max_chunk_count_generator(chunk_count, file_data):
    chunk_size = len(file_data) // chunk_count
    return chunk_generator(chunk_count, chunk_size, file_data)
