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

nnoremap <silent> <Plug>(NvGdbReset) :NvGdbReset<Return>
nnoremap <silent> <Plug>(NvGdbRefreshBreakpoints) :NvGdbRefreshBreakpoints<Return>
nnoremap <silent> <Plug>(NvGdbEvalWord) :NvGdbEvalWord<Return>

function NvGdbFloatingWindow(inp_str, in_width, in_height)
    let buf = nvim_create_buf(v:false, v:true)
    call nvim_buf_set_lines(buf, 0, -1, v:true, a:inp_str)
    let opts = {'relative': 'cursor', 'width': a:in_width, 'height': a:in_height, 'col': 0,
        \ 'row': 1, 'anchor': 'NW', 'style': 'minimal'}
    let win = nvim_open_win(buf, 0, opts)
    " optional: change highlight, otherwise Pmenu is used
    " call nvim_win_set_option(win, 'winhl', 'Normal:MyHighlight')
endfunction
