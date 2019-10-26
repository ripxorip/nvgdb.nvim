# ============================================================================
# FILE: nvgdb.py
# AUTHOR: Philip Karlsson Gisslow <philipkarlsson at me.com>
# License: MIT license
# ============================================================================

import os
import subprocess

class NvGdb(object):
    def __init__(self):
        self.logstr = []
        self.logstr.append('== NvGdb debug log ==')

    def log(self, s):
        if '\n' in s:
            ns = s.split('\n')
            for i in ns:
                self.logstr.append(i)
        else:
            self.logstr.append(str(s))

    def get_log(self):
        return self.logstr
