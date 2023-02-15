# -*- coding: utf-8 -*-
# Python 3

from xstream import run
from os.path import join
from sys import path
import platform

from resources.lib import common
from resources.lib.tools import logger

_addonPath_ = common.addonPath
path.append(join(_addonPath_, 'resources', 'lib'))
path.append(join(_addonPath_, 'resources', 'lib', 'gui'))
path.append(join(_addonPath_, 'resources', 'lib', 'handler'))
path.append(join(_addonPath_, 'resources', 'art', 'sites'))
path.append(join(_addonPath_, 'resources', 'art'))
path.append(join(_addonPath_, 'sites'))
logger.info('*---- Start xStream Log, Version %s ----*' % common.addon.getAddonInfo('version'))
logger.info('Python-Version: %s' % platform.python_version())

try:
    run()
except Exception as e:
    if str(e) == 'UserAborted':
        logger.error('User aborted list creation')
    else:
        import traceback
        import xbmcgui
        logger.error(traceback.format_exc())
        value = (str(e.__class__.__name__) + ' : ' + str(e), str(traceback.format_exc().splitlines()[-3].split('addons')[-1]))
        dialog = xbmcgui.Dialog().ok('Error', str(value))
