# Copyright 2013 Hynek Schlawack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Processors and helpers specific to the `logging module
<http://docs.python.org/2/library/logging.html>`_ from the `Python standard
library <http://docs.python.org/>`_.
"""

from __future__ import absolute_import, division, print_function

import logging
import sys

from structlog._base import BoundLoggerBase
from structlog._exc import DropEvent


class BoundLogger(BoundLoggerBase):
    """
    Python Standard Library version of :class:`structlog.BoundLogger`.
    Works exactly like the generic one except that it takes advantage of
    knowing the logging methods in advance.

    Use it like::

        configure(
            wrapper_class=structlog.stdlib.BoundLogger,
        )

    """
    def debug(self, event=None, **kw):
        """
        Process event and call ``Logger.debug()`` with the result.
        """
        return self._proxy_to_logger('debug', event, **kw)

    def info(self, event=None, **kw):
        """
        Process event and call ``Logger.info()`` with the result.
        """
        return self._proxy_to_logger('info', event, **kw)

    def warning(self, event=None, **kw):
        """
        Process event and call ``Logger.warning()`` with the result.
        """
        return self._proxy_to_logger('warning', event, **kw)

    warn = warning

    def error(self, event=None, **kw):
        """
        Process event and call ``Logger.error()`` with the result.
        """
        return self._proxy_to_logger('error', event, **kw)

    def critical(self, event=None, **kw):
        """
        Process event and call ``Logger.critical()`` with the result.
        """
        return self._proxy_to_logger('critical', event, **kw)


class LoggerFactory(object):
    """
    Build a standard library logger when an *instance* is called.

    >>> from structlog import configure
    >>> from structlog.stdlib import LoggerFactory
    >>> configure(logger_factory=LoggerFactory())
    """
    def __call__(self):
        """
        Deduces the caller's module name and create a stdlib logger.

        :rtype: `logging.Logger`
        """
        f = sys._getframe()
        name = f.f_globals['__name__']

        # We skip all frames that originate from within structlog.
        while name.startswith('structlog.'):
            f = f.f_back
            name = f.f_globals['__name__']
        return logging.getLogger(name)


# Adapted from the stdlib

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_nameToLevel = {
    'critical': CRITICAL,
    'error': ERROR,
    'warn': WARNING,
    'warning': WARNING,
    'info': INFO,
    'debug': DEBUG,
    'notset': NOTSET,
}


def filter_by_level(logger, name, event_dict):
    """
    Check whether logging is configured to accept messages from this log level.

    Should be the first processor if stdlib's filtering by level is used so
    possibly expensive processors like exception formatters are avoided in the
    first place.

    >>> import logging
    >>> from structlog.stdlib import filter_by_level
    >>> logging.basicConfig(level=logging.WARN)
    >>> logger = logging.getLogger()
    >>> filter_by_level(logger, 'warn', {})
    {}
    >>> filter_by_level(logger, 'debug', {})
    Traceback (most recent call last):
    ...
    DropEvent
    """
    if logger.isEnabledFor(_nameToLevel[name]):
        return event_dict
    else:
        raise DropEvent
