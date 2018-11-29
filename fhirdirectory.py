
import requests
from six.moves.html_parser import HTMLParser
from six.moves.urllib.parse import urljoin, urlparse
from collections import namedtuple
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)


def cleandata(data):
    if data.startswith('('):
        return data.strip()[1:-1]
    else:
        return data.strip()


class FHIRPackageList:

    URL = "http://hl7.org/fhir/package-list.json"

    def __init__(self):
        self._versions = []
        self._implementation_guides = []

    @property
    def versions(self):
        if not self._versions:
            self.get()
        return self._versions

    @property
    def implementation_guides(self):
        if not self._implementation_guides:
            self.get()
        return self._implementation_guides

    def get(self):
        """
        Download the metadata
        """
        sess = requests.Session()
        response = sess.get(self.URL)
        if response.status_code == 200:
            content = response.json()
            for version in content.get('list'):
                parts = urlparse(version.get('path'))   # type: urllib.parse.ParseResult
                if parts.path == "":
                    symbol = "latest"
                else:
                    symbol = parts.path.split("/")[-1]
                _current = dict(Link=version.get('path'),
                                Version=version.get('version'),
                                Date=version.get('date'),
                                Description=version.get('desc'),
                                Status=version.get('status'),
                                Symbol=symbol,
                                Sequence=version.get('sequence', 'Unknown'))
                current = namedtuple("FHIRRelease", _current.keys())(**_current)
                self._versions.append(current)
            # load the implementation guides
            for ig in content.get("containedIgs"):
                self._implementation_guides.append(ig)
        else:
            raise ValueError("Unable to retrieve the FHIR Versions")


def get_versions():
    """
    Download the versions from the FHIR Directory URL
    :return:
    """
    package = FHIRPackageList()
    return package.versions

