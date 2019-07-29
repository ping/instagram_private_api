import sys
import urllib.request as request
import json
from os import path

package_name = 'instapi'
here = path.abspath(path.dirname(__file__))

def readall(*args):
    with open(path.join(here, *args), encoding='utf-8') as fp:
        return fp.read()

def writeall(*args, content):
    with open(path.join(here, *args), 'w+', encoding='utf-8') as fp:
        return fp.write(content)

def bump():
    response = request.urlopen(f'https://pypi.org/pypi/{package_name}/json')
    res = response.read()
    res_json = json.loads(res)
    releases = res_json['releases']

    version = readall(f'../{package_name}', 'version.txt')
    print('current version: ', version)

    # version does not exist so do not bump
    if version not in releases: return

    # bump version
    v_split = version.split('.')
    patch = v_split[2]
    patch = str(int(patch) + 1)
    v_split[2] = patch
    new_version = '.'.join(v_split)

    print('new version: ', new_version)

    writeall(f'../{package_name}', 'version.txt', content = new_version)


if __name__ == '__main__':
    try:
        bump()
    except Exception as e:
        print('Exception bumping version!')
        print(e)

    # clean exit no matter what
    sys.exit(0)