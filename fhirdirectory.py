import requests
from six.moves.html_parser import HTMLParser
from six.moves.urllib.parse import urljoin
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

    @property
    def versions(self):
        if not self._versions:
            self.get()
        return self._versions

    def get(self):
        """
        Download the metadata
        """
        sess = requests.Session()
        response = sess.get(self.URL)
        if response.status_code == 200:
            content = response.json()
            for version in content.get('list'):
                _current = dict(Link=version.get('path'),
                                Version=version.get('version'),
                                Date=version.get('date'),
                                Description=version.get('desc'),
                                Status=version.get('status'))
                current = namedtuple("FHIRRelease", _current.keys())(**_current)
                self._versions.append(current)
        else:
            raise ValueError("Unable to retrieve the FHIR Versions")


class DirectoryParser(HTMLParser):
    """
    Parses the returned value from http://hl7.org/fhir/directory.html
    """
    # NOTE: current requests does not like the SSL implementation
    #  on hl7.org - this should be updated when TLS1.2 has been implemented
    URL = "http://hl7.org/fhir/directory.html"

    ATTR = ('Link', 'Date', 'Version', 'Description')

    def error(self, message):
        logger.error("Unable to parse; Error: {}".format(message))

    def __init__(self):
        super(DirectoryParser, self).__init__()
        self.is_row = False
        self.is_col = False
        self.is_version = False
        self.is_release = False
        self._versions = []
        self._current_release = None
        self._current = None

    def get(self):
        sess = requests.Session()
        response = sess.get(self.URL, verify=False)
        if response.status_code == 200:
            content = response.content
            if hasattr(content, 'decode'):
                content = content.decode('ISO-8859-1')
            self.feed(content)

    @property
    def versions(self):
        if not self._versions:
            self.get()
        return self._versions

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.is_row = True
            # Create the stack
            self._current = dict()
        _attrs = dict(attrs)
        if tag == 'td' and not 'colspan' in _attrs:
            self.is_col = True
        if tag == 'td' and 'colspan' in _attrs:
            self.is_release = True
        if self.is_col and tag == 'a':
            self.is_version = True
            # set the link
            if not _attrs.get('href').startswith('http'):
                link = urljoin(self.URL, _attrs.get('href'))
            else:
                link = _attrs.get('href')
            self._current['Link'] = link

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.is_row = False
            if self._current and not self._current['Date'] == 'Version':
                if self._current['Link'] == 'http://hl7.org/fhir/2012Sep/index.htm':
                    # Aberrant HTML
                    _current = dict(Link='http://hl7.org/fhir/2012Sep/index.htm',
                                    Version="0.05",
                                    Date="Sep 9, 2012",
                                    Description="1st Draft for Comment (Sept 2012 Ballot)",
                                    Release="DSTU 1 sequence")
                    current = namedtuple("FHIRRelease", _current.keys())(**_current)
                else:
                    # Add the release designation
                    self._current['Release'] = self._current_release
                    current = namedtuple("FHIRRelease", self._current.keys())(**self._current)
                self._versions.append(current)
        if tag == 'td':
            if self.is_release:
                self.is_release = False
            if self.is_col:
                self.is_col = False
        if self.is_version and tag == 'a':
            self.is_version = False

    def handle_data(self, data):
        if self.is_col:
            if self.is_version:
                self._current['Date'] = cleandata(data)
            else:
                for attr in self.ATTR:
                    if attr not in self._current:
                        self._current[attr] = cleandata(data)
                        # only want to set one attribute at a time
                        break
        if self.is_release:
            self._current_release = cleandata(data)


def get_versions():
    """
    Download the versions from the FHIR Directory URL
    :return:
    """
    package = FHIRPackageList()
    if package.versions:
        return package.versions
    else:
        package = DirectoryParser()
        return package.versions
