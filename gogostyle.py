##############################################################################
#
# gogostyle.py <tim@tbrk.org>
#
# Plugin for applying regular expression substitutions during Mnemogogo
# export.
#
# This plugin allows certain characters to be displayed using a different font,
# style, or size under Mnemododo. (i.e. on Android phones using data exported
# from Mnemosyne.)
#
# Basic use
# ---------
# 1. Install the plugin under Mnemosyne, note that it only takes effect during
#    an export from Mnemogogo.
#
# 2. Add a STYLE.CSS file to your Mnemogogo export directory, with
#    css declarations to restyle the spans added by this plugin, e.g.:
#       span.thai { font-size: 500% }
#
# Intermediate use
# ----------------
# Edit the config.py file that exists under the Mnemosyne home directory
# ($HOME/.mnemosyne), and add an entry similar to:
# gogostyles = [
#       (ur'([\u0E00-\u0E7F]+)', r'<span class="thai">\1</span>'),
# ]
#
# Replace the unicode range on the left and the class name on the right.
#
# History
# -------
# version 1.0.0
#   * initial release
# Version 1.1.0
#   * added cjk punctuation, thanks to Nils von Barth
# Version 1.1.1
#   * added cjk full and half-width forms, thanks to Nils von Barth
# Version 1.1.2
#   * Fix a bug that causes the config file to grow at each initialisation.
#     Thanks to Nils von Barth for noticing and diagnosing this problem.
# Version 2.0.0
#   * Updated for Mnemosyne 2.x
#
##############################################################################

try:
  from mnemosyne.core import *
  mnemosyne_version = 1

except ImportError:
  mnemosyne_version = 2
  from PyQt4 import QtCore, QtGui
  from mnemosyne.libmnemosyne.hook import Hook
  from mnemosyne.libmnemosyne.filter import Filter
  from mnemosyne.libmnemosyne.plugin import Plugin
  from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
       ConfigurationWidget

import re

name = "Gogostyle"
version = "2.0.0"
description = "Wrap characters in CSS tags during Mnemogogo export. (v" + version + ")"

# conversions should not overlap.
# please email tim@tbrk.org if there are errors in this default table,
# or if you would like something else added.
# NB: you can add personal stylings in config.py
default_styles = [
        # ( regex ,        replacement )
        (ur'([\u0E00-\u0E7F]+)', r'<span class="thai">\1</span>'),
        (ur'([\u0370-\u03FF]+)', r'<span class="greekandcoptic">\1</span>'),
        (ur'([\u0600-\u06FF]+)', r'<span class="arabic">\1</span>'),
        (ur'([\u0590-\u05FF]+)', r'<span class="hebrew">\1</span>'),
        (ur'([\u3040-\u309F]+)', r'<span class="hiragana">\1</span>'),
        (ur'([\u30A0-\u30FF]+)', r'<span class="katakana">\1</span>'),
        (ur'([\u4E00-\u9FFF]+)', r'<span class="cjk">\1</span>'),
        (ur'([\u3000-\u303F]+)', r'<span class="cjk">\1</span>'), # cjk punctuation
        (ur'([\uFF00-\uFFEF]+)', r'<span class="cjk">\1</span>'), # cjk full and half-width forms
        (ur'([\u1100-\u11FF]+)', r'<span class="hangul">\1</span>'),
        (ur'([\uAC00-\uD7AF]+)', r'<span class="hangul">\1</span>'),
    ]

render_chains = ["mnemogogo"]

def compile_styles(styles):
    results = []
    for (mat, rep) in styles:
        try:
            results.append(
                (re.compile(mat, re.DOTALL | re.IGNORECASE), rep))
        except re.error as e:
            pass

    return results

def format(text, conversions):
    for (mat, rep) in conversions:
        text = mat.sub(rep, text)
    return text

##############################################################################
# Mnemosyne 1.x
if mnemosyne_version == 1:

    class Gogostyle(Plugin):

        name = name
        version = version

        def description(self):
            return description

        def load(self):
            self.format_mnemosyne = False
            self.format_mnemogogo = True

            try: gogostyles = list(get_config("gogostyles"))
            except KeyError:
                gogostyles = []
                set_config("gogostyles", [])

            gogostyles.extend(default_styles)
            self.conversions = compile_styles(gogostyles)

            if (self.format_mnemosyne):
                register_function_hook("filter_q", self.run)
                register_function_hook("filter_a", self.run)

            if (self.format_mnemogogo):
                register_function_hook("gogo_q", self.run)
                register_function_hook("gogo_a", self.run)

        def unload(self):
            if (self.format_mnemosyne):
                unregister_function_hook("filter_q", self.run)
                unregister_function_hook("filter_a", self.run)

            if (self.format_mnemogogo):
                unregister_function_hook("gogo_q", self.run)
                unregister_function_hook("gogo_a", self.run)
        
        def run(self, text, card):
            return format(text, self.conversions)

    p = Gogostyle()
    p.load()

##############################################################################
# Mnemosyne 2.x
elif mnemosyne_version == 2:

    class GogoStyle(Filter):
        name = name
        version = version
        conversions = None

        def __init__(self, component_manager):
            Filter.__init__(self, component_manager)
            self.reconfigure()

        def reconfigure(self):
            try:
                styles = self.config()["styles"]
            except KeyError:
                styles = default_styles
            self.conversions = compile_styles(styles)

        def run(self, text, card, fact_key, **render_args):
            return format(text, self.conversions)

    class GogoStylePlugin(Plugin):
        name = name
        description = description
        components = [GogoStyle]

        def __init__(self, component_manager):
            Plugin.__init__(self, component_manager)

        def activate(self):
            Plugin.activate(self)
            for chain in render_chains:
                try:
                    self.new_render_chain(chain)
                except KeyError: pass

        def deactivate(self):
            Plugin.deactivate(self)
            for chain in render_chains:
                try:
                    self.render_chain(chain).unregister_filter(GogoStyle)
                except KeyError: pass

        def new_render_chain(self, name):
            if name in render_chains:
                self.render_chain(name).register_filter_at_back(
                        GogoStyle, before=["ExpandPaths"])

    # Register plugin.

    from mnemosyne.libmnemosyne.plugin import register_user_plugin
    register_user_plugin(GogoStylePlugin)

