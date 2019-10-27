" Author: Philip <philipkarlsson@me.com>
" Description: Main entry point for the plugin: sets up prefs and autocommands
"   Preferences can be set in vimrc files and so on to configure aerojump

nnoremap <silent> <Plug>(NvGdbStart) :NvGdbStart<Return>
nnoremap <silent> <Plug>(NvGdbToggleBreakpoint) :NvGdbToggleBreakpoint<Return>
nnoremap <silent> <Plug>(NvGdbShowLog) :NvGdbShowLog<Return>

nnoremap <silent> <Plug>(NvGdbSingleStep) :NvGdbSingleStep<Return>
nnoremap <silent> <Plug>(NvGdbStepOver) :NvGdbStepOver<Return>
nnoremap <silent> <Plug>(NvGdbResume) :NvGdbResume<Return>
nnoremap <silent> <Plug>(NvGdbStop) :NvGdbStop<Return>
