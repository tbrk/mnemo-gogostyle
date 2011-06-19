##############################################################################
#
# gogostyle.py
# Timothy Bourke <tim@tbrk.org>
#
# Plugin for applying regular expression substitutions during Mnemogogo
# export.
#
# The main reason for this plugin is to allow certain characters to be
# displayed using a different font, style, or size under Mnemododo.
# (i.e. on Android phones using data exported from Mnemosyne.)
#
# Basic use
# ---------
# 1. Save this file into the Mnemosyne plugins directory
#    ($HOME/.mnemosyne/plugins) and start Mnemosyne.
# The plugin only takes effect during a Mnemogogo export.
#
# 2. Add a STYLE.CSS file to your Mnemogogo export directory, with
#    css declarations to restyle the spans added by this plugin, e.g.:
#	span.thai { font-size: 500% }
#
# Intermediate use
# ----------------
# Edit the config.py file that exists under the Mnemosyne home directory
# ($HOME/.mnemosyne), and add an entry similar to:
# gogostyles = [
#	(ur'([\u0E00-\u0E7F]+)', r'<span class="thai">\1</span>'),
# ]
#
# Replace the unicode range on the left and the class name on the right.
#
# History
# -------
# version 1.0.0
#   * initial release
# Version 1.1
#   * added cjk punctuation, thanks to Nils von Barth
# Version 1.1
#   * added cjk full and half-width forms, thanks to Nils von Barth
#
##############################################################################

from mnemosyne.core import *
import re

name = "gogostyle"
version = "1.1.0"

# conversions should not overlap.
# please email tim@tbrk.org if there are errors in this default table,
# or if you would like something else added.
# NB: you can add personal stylings in config.py
default_styles = [
	# ( regex ,	   replacement )
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

class Gogostyle(Plugin):

    def description(self):
	return ("Apply regular expressions during Mnemogogo export. (v" +
		version + ")")

    def load(self):
	self.format_mnemosyne = False
	self.format_mnemogogo = True

	try: self.gogostyles = get_config("gogostyles")
	except KeyError:
	    self.gogostyles = []
	    set_config("gogostyles", [])

	self.gogostyles.extend(default_styles)
	self.conversions = []

	if (self.format_mnemosyne):
	    register_function_hook("filter_q", self.format)
	    register_function_hook("filter_a", self.format)

	if (self.format_mnemogogo):
	    register_function_hook("gogo_q", self.format)
	    register_function_hook("gogo_a", self.format)

    def unload(self):
	if (self.format_mnemosyne):
	    unregister_function_hook("filter_q", self.format)
	    unregister_function_hook("filter_a", self.format)

	if (self.format_mnemogogo):
	    unregister_function_hook("gogo_q", self.format)
	    unregister_function_hook("gogo_a", self.format)
    
    def format(self, text, card):
	if not self.conversions:
	    for (mat, rep) in self.gogostyles:
		self.conversions.append(
		    (re.compile(mat, re.DOTALL | re.IGNORECASE), rep))

	for (mat, rep) in self.conversions:
	    text = mat.sub(rep, text)

	return text

p = Gogostyle()
p.load()

