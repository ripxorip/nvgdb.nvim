# ============================================================================
# FILE: __init__.py
# AUTHOR: Philip Karlsson Gisslow <philipkarlsson at me.com>
# License: MIT license
# ============================================================================

import neovim
import time
import threading

from nvgdb.nvgdb import NvGdb

@neovim.plugin
class NvGdbWrapper(object):
    def __init__(self, nvim):
        self.nvim = nvim
        self.ng = NvGdb(nvim)

    def server_wrapper(self):
        self.ng.serve()

    @neovim.command("NvGdbStart", range='', nargs='*', sync=True)
    def NvGdbStart(self, args, range):
        t = threading.Thread(target=self.server_wrapper, daemon=True)
        t.start()

    @neovim.command("NvGdbToggleBreakpoint", range='', nargs='*', sync=True)
    def NvGdbToggleBreakpoint(self, args, range):
        # Get current line and file
        currentLine = self.nvim.command_output('echo line(".")')
        currentFile = self.nvim.command_output('echo expand("%:p")')
        self.ng.toggle_breakpoint(currentFile, currentLine)

    @neovim.command("NvGdbSingleStep", range='', nargs='*', sync=True)
    def NvGdbSingleStep(self, args, range):
        self.ng.single_step()

    @neovim.command("NvGdbStepOver", range='', nargs='*', sync=True)
    def NvGdbStepOver(self, args, range):
        self.ng.step_over()

    @neovim.command("NvGdbStop", range='', nargs='*', sync=True)
    def NvGdbStop(self, args, range):
        self.ng.stop()

    @neovim.command("NvGdbResume", range='', nargs='*', sync=True)
    def NvGdbResume(self, args, range):
        self.ng.resume()

    @neovim.command("NvGdbReset", range='', nargs='*', sync=True)
    def NvGdbReset(self, args, range):
        self.ng.reset()

    @neovim.command("NvGdbRefreshBreakpoints", range='', nargs='*', sync=True)
    def NvGdbRefreshBreakpoints(self, args, range):
        self.ng.refresh_breakpoints()

    @neovim.command("NvGdbEvalWord", range='', nargs='*', sync=True)
    def NvGdbEvalWord(self, args, range):
        self.ng.eval_word()

    @neovim.command("NvGdbShowStackTrace", range='', nargs='*', sync=True)
    def NvGdbShowStackTrace(self, args, range):
        self.ng.show_stack_trace()

    @neovim.command("NvGdbSelectStackFrame", range='', nargs='*', sync=True)
    def NvGdbSelectStackFrame(self, args, range):
        self.ng.select_stack_frame_from_stack_window()

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
