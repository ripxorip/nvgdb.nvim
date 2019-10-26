# ============================================================================
# FILE: __init__.py
# AUTHOR: Philip Karlsson Gisslow <philipkarlsson at me.com>
# License: MIT license
# ============================================================================

import neovim

from nvgdb.nvgdb import NvGdb

@neovim.plugin
class NvGdb(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.ng = NvGdb()

    @neovim.command("NvGdbStart", range='', nargs='*', sync=True)
    def NvGdbStart(self, args, range):
        self.ng.log('Test')

    @neovim.command("NvGdbShowLog", range='', nargs='*', sync=True)
    def NvGdbShowLog(self, args, range):
        """ Show the R2Nvim log

        Parameters:
            n/a

        Returns:
            n/a
        """
        self.nvim.command('e NvGdb_log')
        self.nvim.command('setlocal buftype=nofile')
        self.nvim.command('setlocal filetype=NvGdb_log')
        logStr = self.ng.get_log()
        self.nvim.current.buffer.append(logStr)
