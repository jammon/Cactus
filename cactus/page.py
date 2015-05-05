import os
import logging
import urlparse

from django.template import Template, Context
from cactus.compat.paths import PageCompatibilityLayer
from cactus.utils.url import ResourceURLHelperMixin
from cactus.utils.helpers import memoize


logger = logging.getLogger(__name__)


class EXTENSIONS:
    html = ['.html']
    markdown = ['.md', '.mdown', '.markdown']
    haml = ['.haml']
    pages = html + markdown + haml

class Page(PageCompatibilityLayer, ResourceURLHelperMixin):

    discarded = False

    def __init__(self, site, source_path):
        self.site = site

        # The path where this element should be linked in "base" pages
        self.source_path = source_path

        # The URL where this element should be linked in "base" pages
        self.link_url = '/' + self.source_path

        # The URL where this element should be linked in "built" pages
        self.final_url = self.link_url

        # The path where this element should be built to
        self.build_path = self.source_path

        path, ext = os.path.splitext(self.source_path.lower())
        self._is_html = ext in EXTENSIONS.pages
        self._is_index = path.endswith('index') and self._is_html
        self._is_markdown = ext in EXTENSIONS.markdown
        self._is_haml = ext in EXTENSIONS.haml

        if self.site.prettify_urls:
            if self._is_html:
                if self._is_index:
                    self.final_url = self.link_url[:-len('index.html')]  # chop 'index.html' off
                else:
                    self.final_url = self.link_url[:-len('.html')] + '/'  # chop '.html' off, add '/'
                    self.build_path = '{0}/{1}'.format(
                            self.source_path[:-len('.html')],
                            'index.html')

    def is_html(self):
        """
        True if page will be built to html
        """
        return self._is_html

    def is_index(self):
        return self._is_index

    def is_markdown(self):
        return self._is_markdown

    def is_haml(self):
        return self._is_haml

    @property
    def absolute_final_url(self):
        """
        Return the absolute URL for this page in the final build
        """
        return urlparse.urljoin(self.site.url, self.final_url)

    @property
    def full_source_path(self):
        return os.path.join(self.site.path, 'pages', self.source_path)

    @property
    def full_build_path(self):
        return os.path.join(self.site.build_path, self.build_path)

    def data(self):
        self._is_binary = False
        with open(self.full_source_path, 'rb') as f:
            try:
                _data = f.read()
                _data = _data.decode('utf-8')
            except IOError:
                logger.error("File %s could not be read", self.full_source_path)
                return None
            except UnicodeDecodeError:
                self._is_binary = True

        return _data

    def context(self, data=None, extra=None):
        """
        The page context.
        """
        if extra is None:
            extra = {}

        context = {'__CACTUS_CURRENT_PAGE__': self,}
        
        page_context, data = self.parse_context(data or self.data())

        context.update(self.site.context())
        context.update(extra)
        context.update(page_context)

        return Context(context)

    def render(self):
        """
        Takes the template data with context and renders it to the final output file.
        """

        data = self.data()

        if self._is_binary:
            return data

        context = self.context(data=data)

        # This is not very nice, but we already used the header context in the
        # page context, so we don't need it anymore.
        page_context, data = self.parse_context(data)

        context, data = self.site.plugin_manager.preBuildPage(
            self.site, self, context, data)

        return Template(data).render(context)

    def build(self):
        """
        Save the rendered output to the output file.
        """
        logger.debug('Building {0} --> {1}'.format(self.source_path, self.final_url))  #TODO: Fix inconsistency w/ static
        data = self.render()  #TODO: This calls preBuild indirectly. Not great.

        if not self.discarded:

            # Make sure a folder for the output path exists
            try:
                os.makedirs(os.path.dirname(self.full_build_path))
            except OSError:
                pass

            with open(self.full_build_path, 'wb') as f:
                f.write(data if self._is_binary
                        else data.encode('utf-8'))

            self.site.plugin_manager.postBuildPage(self)

    def parse_context(self, data, splitChar=':'):
        """
        Values like

        name: koen
        age: 29

        will be converted in a dict: {'name': 'koen', 'age': '29'}
        """

        if not self.is_html():
            return {}, data

        values = {}
        lines = data.splitlines()
        if not lines:
            return {}, ''

        for i, line in enumerate(lines):

            if not line:
                continue

            elif splitChar in line:
                line = line.split(splitChar)
                values[line[0].strip()] = (splitChar.join(line[1:])).strip()

            else:
                break

        return values, '\n'.join(lines[i:])

    def __repr__(self):
        return '<Page: {0}>'.format(self.source_path)
