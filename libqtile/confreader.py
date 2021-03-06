#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2008, Aldo Cortesi <aldo@corte.si>
# Copyright (c) 2011, Andrew Grigorev <andrew@ei-grad.ru>
#
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import logging
from imp import new_module
from libqtile import manager, layout
from libqtile.command import lazy
from .layout import Floating


class ConfigError(Exception):
    pass


# Default / fallback config
class Config:
    keys = [
        manager.Key(['mod4'], "Tab", lazy.layout.next()),
        manager.Key(['mod4'], "q", lazy.restart())
    ]
    mouse = ()
    groups = [manager.Group('fallback'), manager.Group('fallback2')]
    layouts = [layout.Tile()]
    screens = [manager.Screen()]
    main = None
    follow_mouse_focus = True
    cursor_warp = False
    floating_layout = Floating()


class File(Config):
    def __init__(self, fname=None):
        if not fname:
            config_directory = os.path.expandvars('$XDG_CONFIG_HOME')
            if config_directory == '$XDG_CONFIG_HOME':
                # if variable wasn't set
                config_directory = os.path.expanduser("~/.config")
            fname = os.path.join(config_directory, "qtile", "config.py")

        self.fname = fname

        if not os.path.isfile(fname):
            raise ConfigError("Config file does not exist: %s" % fname)

        config = new_module('config')
        config.__file__ = fname
        try:
            sys.path.insert(0, os.path.dirname(fname))
            execfile(config.__file__, config.__dict__)
        except Exception:
            logging.getLogger('qtile').exception('Config error')
            raise ConfigError()

        self.screens = config.screens
        self.layouts = config.layouts
        self.keys = config.keys
        self.groups = config.groups
        self.mouse = getattr(config, "mouse", [])
        self.follow_mouse_focus = getattr(config, "follow_mouse_focus", True)
        self.cursor_warp = getattr(config, "cursor_warp", False)
        self.floating_layout = getattr(config, 'floating_layout', None)
        if self.floating_layout is None:
            from .layout import Floating
            self.floating_layout = Floating()
        self.main = getattr(config, "main", None)
        # Keep it so local vars don't get decref
        self.config_module = config
