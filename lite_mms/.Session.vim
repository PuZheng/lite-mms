let SessionLoad = 1
if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
inoremap <silent> <S-Tab> =BackwardsSnippet()
inoremap <Plug>ZenCodingAnchorizeSummary :call zencoding#anchorizeURL(1)a
inoremap <Plug>ZenCodingAnchorizeURL :call zencoding#anchorizeURL(0)a
inoremap <Plug>ZenCodingRemoveTag :call zencoding#removeTag()a
inoremap <Plug>ZenCodingSplitJoinTagInsert :call zencoding#splitJoinTag()a
inoremap <Plug>ZenCodingToggleComment :call zencoding#toggleComment()a
inoremap <Plug>ZenCodingImageSize :call zencoding#imageSize()a
inoremap <Plug>ZenCodingPrev :call zencoding#moveNextPrev(1)
inoremap <Plug>ZenCodingNext :call zencoding#moveNextPrev(0)
inoremap <Plug>ZenCodingBalanceTagOutwardInsert :call zencoding#balanceTag(-1)a
inoremap <Plug>ZenCodingBalanceTagInwardInsert :call zencoding#balanceTag(1)a
inoremap <Plug>ZenCodingExpandWord u:call zencoding#expandAbbr(1)a
inoremap <Plug>ZenCodingExpandAbbr u:call zencoding#expandAbbr(0)a
imap <silent> <Plug>IMAP_JumpBack =IMAP_Jumpfunc('b', 0)
imap <silent> <Plug>IMAP_JumpForward =IMAP_Jumpfunc('', 0)
inoremap <silent> <Plug>NERDCommenterInInsert  <BS>:call NERDComment(0, "insert")
noremap ra :call RopeAutoImport()
map rd :RopeShowDoc
map d :call RopeShowDoc()
map f :call RopeFindOccurrences()
map g :call RopeGotoDefinition()
noremap ru :call RopeUseFunction()
noremap rad :call RopeShowDoc()
noremap rac :call RopeShowCalltip()
noremap rx :call RopeRestructure()
noremap r1r :call RopeRenameCurrentModule()
noremap rr :call RopeRename()
noremap ro :call RopeOrganizeImports()
noremap r1v :call RopeMoveCurrentModule()
noremap rv :call RopeMove()
noremap r1p :call RopeModuleToPackage()
noremap ra? :call RopeLuckyAssist()
noremap raj :call RopeJumpToGlobal()
noremap rf :call RopeIntroduceFactory()
noremap ri :call RopeInline()
noremap rag :call RopeGotoDefinition()
noremap rnv :call RopeGenerateVariable()
noremap rnp :call RopeGeneratePackage()
noremap rnm :call RopeGenerateModule()
noremap rnf :call RopeGenerateFunction()
noremap rnc :call RopeGenerateClass()
noremap raf :call RopeFindOccurrences()
noremap rai :call RopeFindImplementations()
noremap rl :call RopeExtractVariable()
noremap rm :call RopeExtractMethod()
noremap ra/ :call RopeCodeAssist()
noremap rs :call RopeChangeSignature()
snoremap <silent> 	 i<Right>=TriggerSnippet()
vmap <NL> <Plug>IMAP_JumpForward
nmap <NL> <Plug>IMAP_JumpForward
nnoremap <silent>  :CtrlP
noremap pg :call RopeGenerateAutoimportCache()
noremap pu :call RopeUndo()
noremap pr :call RopeRedo()
noremap pc :call RopeProjectConfig()
noremap po :call RopeOpenProject()
noremap p4f :call RopeFindFileOtherWindow()
noremap pf :call RopeFindFile()
noremap pnp :call RopeCreatePackage()
noremap pnm :call RopeCreateModule()
noremap pnf :call RopeCreateFile()
noremap pnd :call RopeCreateDirectory()
noremap pk :call RopeCloseProject()
snoremap  b<BS>
nmap A <Plug>ZenCodingAnchorizeSummary
nmap a <Plug>ZenCodingAnchorizeURL
nmap k <Plug>ZenCodingRemoveTag
nmap j <Plug>ZenCodingSplitJoinTagNormal
nmap / <Plug>ZenCodingToggleComment
nmap i <Plug>ZenCodingImageSize
nmap N <Plug>ZenCodingPrev
nmap n <Plug>ZenCodingNext
vmap D <Plug>ZenCodingBalanceTagOutwardVisual
nmap D <Plug>ZenCodingBalanceTagOutwardNormal
vmap d <Plug>ZenCodingBalanceTagInwardVisual
nmap d <Plug>ZenCodingBalanceTagInwardNormal
nmap ; <Plug>ZenCodingExpandWord
nmap , <Plug>ZenCodingExpandNormal
vmap , <Plug>ZenCodingExpandVisual
snoremap % b<BS>%
snoremap ' b<BS>'
nnoremap ,- yyp$r-
nnoremap ,~ yyp$r~
nnoremap ,= yyp$r=
map ,h :Dbg here
map ,b :Dbg break
map ,w :Dbg watch
map ,u :Dbg up
map ,r :Dbg run
map ,i :Dbg into
map ,o :Dbg over
nmap ,ca <Plug>NERDCommenterAltDelims
vmap ,cA <Plug>NERDCommenterAppend
nmap ,cA <Plug>NERDCommenterAppend
vmap ,c$ <Plug>NERDCommenterToEOL
nmap ,c$ <Plug>NERDCommenterToEOL
vmap ,cu <Plug>NERDCommenterUncomment
nmap ,cu <Plug>NERDCommenterUncomment
vmap ,cn <Plug>NERDCommenterNest
nmap ,cn <Plug>NERDCommenterNest
vmap ,cb <Plug>NERDCommenterAlignBoth
nmap ,cb <Plug>NERDCommenterAlignBoth
vmap ,cl <Plug>NERDCommenterAlignLeft
nmap ,cl <Plug>NERDCommenterAlignLeft
vmap ,cy <Plug>NERDCommenterYank
nmap ,cy <Plug>NERDCommenterYank
vmap ,ci <Plug>NERDCommenterInvert
nmap ,ci <Plug>NERDCommenterInvert
vmap ,cs <Plug>NERDCommenterSexy
nmap ,cs <Plug>NERDCommenterSexy
vmap ,cm <Plug>NERDCommenterMinimal
nmap ,cm <Plug>NERDCommenterMinimal
vmap ,c  <Plug>NERDCommenterToggle
nmap ,c  <Plug>NERDCommenterToggle
vmap ,cc <Plug>NERDCommenterComment
nmap ,cc <Plug>NERDCommenterComment
map ,p :e ~/.temp
map ,m :e ~/.memo
map ,q :e ~/.question
map ,d :e ~/.digest
map ,t :e ~/.todo
map ,e :e ~/.vimrc
imap ¿ =RopeLuckyAssistInsertMode()
imap ¯ =RopeCodeAssistInsertMode()
snoremap U b<BS>U
vmap [% [%m'gv``
snoremap \ b<BS>\
vmap ]% ]%m'gv``
snoremap ^ b<BS>^
snoremap ` b<BS>`
vmap a% [%v]%
nmap gx <Plug>NetrwBrowseX
snoremap <Left> bi
snoremap <Right> a
snoremap <BS> b<BS>
snoremap <silent> <S-Tab> i<Right>=BackwardsSnippet()
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#NetrwBrowseX(expand("<cWORD>"),0)
nnoremap <Plug>ZenCodingAnchorizeSummary :call zencoding#anchorizeURL(1)
nnoremap <Plug>ZenCodingAnchorizeURL :call zencoding#anchorizeURL(0)
nnoremap <Plug>ZenCodingRemoveTag :call zencoding#removeTag()
nnoremap <Plug>ZenCodingSplitJoinTagNormal :call zencoding#splitJoinTag()
nnoremap <Plug>ZenCodingToggleComment :call zencoding#toggleComment()
nnoremap <Plug>ZenCodingImageSize :call zencoding#imageSize()
nnoremap <Plug>ZenCodingPrev :call zencoding#moveNextPrev(1)
nnoremap <Plug>ZenCodingNext :call zencoding#moveNextPrev(0)
vnoremap <Plug>ZenCodingBalanceTagOutwardVisual :call zencoding#balanceTag(-2)
nnoremap <Plug>ZenCodingBalanceTagOutwardNormal :call zencoding#balanceTag(-1)
vnoremap <Plug>ZenCodingBalanceTagInwardVisual :call zencoding#balanceTag(2)
nnoremap <Plug>ZenCodingBalanceTagInwardNormal :call zencoding#balanceTag(1)
nnoremap <Plug>ZenCodingExpandWord :call zencoding#expandAbbr(1)
nnoremap <Plug>ZenCodingExpandNormal :call zencoding#expandAbbr(3)
vnoremap <Plug>ZenCodingExpandVisual :call zencoding#expandAbbr(2)
vmap <silent> <Plug>IMAP_JumpBack `<i=IMAP_Jumpfunc('b', 0)
vmap <silent> <Plug>IMAP_JumpForward i=IMAP_Jumpfunc('', 0)
vmap <silent> <Plug>IMAP_DeleteAndJumpBack "_<Del>i=IMAP_Jumpfunc('b', 0)
vmap <silent> <Plug>IMAP_DeleteAndJumpForward "_<Del>i=IMAP_Jumpfunc('', 0)
nmap <silent> <Plug>IMAP_JumpBack i=IMAP_Jumpfunc('b', 0)
nmap <silent> <Plug>IMAP_JumpForward i=IMAP_Jumpfunc('', 0)
nmap <silent> <Plug>NERDCommenterAppend :call NERDComment(0, "append")
nnoremap <silent> <Plug>NERDCommenterToEOL :call NERDComment(0, "toEOL")
vnoremap <silent> <Plug>NERDCommenterUncomment :call NERDComment(1, "uncomment")
nnoremap <silent> <Plug>NERDCommenterUncomment :call NERDComment(0, "uncomment")
vnoremap <silent> <Plug>NERDCommenterNest :call NERDComment(1, "nested")
nnoremap <silent> <Plug>NERDCommenterNest :call NERDComment(0, "nested")
vnoremap <silent> <Plug>NERDCommenterAlignBoth :call NERDComment(1, "alignBoth")
nnoremap <silent> <Plug>NERDCommenterAlignBoth :call NERDComment(0, "alignBoth")
vnoremap <silent> <Plug>NERDCommenterAlignLeft :call NERDComment(1, "alignLeft")
nnoremap <silent> <Plug>NERDCommenterAlignLeft :call NERDComment(0, "alignLeft")
vmap <silent> <Plug>NERDCommenterYank :call NERDComment(1, "yank")
nmap <silent> <Plug>NERDCommenterYank :call NERDComment(0, "yank")
vnoremap <silent> <Plug>NERDCommenterInvert :call NERDComment(1, "invert")
nnoremap <silent> <Plug>NERDCommenterInvert :call NERDComment(0, "invert")
vnoremap <silent> <Plug>NERDCommenterSexy :call NERDComment(1, "sexy")
nnoremap <silent> <Plug>NERDCommenterSexy :call NERDComment(0, "sexy")
vnoremap <silent> <Plug>NERDCommenterMinimal :call NERDComment(1, "minimal")
nnoremap <silent> <Plug>NERDCommenterMinimal :call NERDComment(0, "minimal")
vnoremap <silent> <Plug>NERDCommenterToggle :call NERDComment(1, "toggle")
nnoremap <silent> <Plug>NERDCommenterToggle :call NERDComment(0, "toggle")
vnoremap <silent> <Plug>NERDCommenterComment :call NERDComment(1, "norm")
nnoremap <silent> <Plug>NERDCommenterComment :call NERDComment(0, "norm")
inoremap <silent> o =VST_Ornaments()
inoremap <silent> 	 =TriggerSnippet()
imap <NL> <Plug>IMAP_JumpForward
imap  
inoremap <silent> 	 =ShowAvailableSnips()
imap A <Plug>ZenCodingAnchorizeSummary
imap a <Plug>ZenCodingAnchorizeURL
imap k <Plug>ZenCodingRemoveTag
imap j <Plug>ZenCodingSplitJoinTagInsert
imap / <Plug>ZenCodingToggleComment
imap i <Plug>ZenCodingImageSize
imap N <Plug>ZenCodingPrev
imap n <Plug>ZenCodingNext
imap D <Plug>ZenCodingBalanceTagOutwardInsert
imap d <Plug>ZenCodingBalanceTagInwardInsert
imap ; <Plug>ZenCodingExpandWord
imap , <Plug>ZenCodingExpandAbbr
map ¿ :call RopeLuckyAssist()
map ¯ :call RopeCodeAssist()
cabbr dbg Dbg
let &cpo=s:cpo_save
unlet s:cpo_save
set autoindent
set background=dark
set backspace=indent,eol,start
set completeopt=menu
set expandtab
set fileencodings=ucs-bom,utf-8,default,latin1
set formatoptions=tcqmM
set guifont=Courier\ 10\ Pitch\ 16
set guioptions=aegiLt
set helplang=cn
set hlsearch
set printoptions=paper:a4
set ruler
set runtimepath=~/.vim/bundle/ctrlp.vim,~/.vim,/var/lib/vim/addons,/usr/share/vim/vimfiles,/usr/share/vim/vim73,/usr/share/vim/vimfiles/after,/var/lib/vim/addons/after,~/.vim/after
set shiftround
set shiftwidth=4
set suffixes=.bak,~,.swp,.o,.info,.aux,.log,.dvi,.bbl,.blg,.brf,.cb,.ind,.idx,.ilg,.inx,.out,.toc
set tabstop=4
set updatetime=1000
set wildignore=*.pyc
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/work/lite-mms-dev/lite-mms/lite_mms
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +4 ~/work/lite-mms-dev/lite-mms/Makefile
badd +17 tools/make_test_data.py
badd +208 utilities/functions.py
badd +19 ~/work/lite-mms-dev/lite-mms/setup.py
badd +66 apis/__init__.py
badd +152 portal/delivery_ws/webservices.py
badd +568 models.py
badd +617 apis/delivery.py
badd +9 database.py
badd +136 test/at/test_delivery.py
badd +146 test/at/steps/delivery.py
badd +489 basemain.py
badd +3 config.py
badd +14 default_settings.py
badd +10 tools/create_codernity_db.py
badd +13 constants/groups.py
badd +85 portal/work_flow/views.py
badd +20 portal/work_flow/__init__.py
badd +130 apis/todo.py
badd +39 portal/cargo/__init__.py
badd +116 portal/cargo/views.py
badd +106 apis/auth.py
badd +202 portal/admin2/views.py
badd +79 portal/cargo/actions.py
badd +39 portal/cargo/fsm.py
badd +327 portal/delivery/views.py
badd +30 portal/order/model_views.py
badd +374 test/at/steps/cargo.py
badd +81 test/at/steps/order.py
badd +59 tools/build_db.py
badd +1 permissions/data.py
badd +10 permissions/work_flow.py
badd +3 permissions/accounts.py
badd +41 permissions/__init__.py
badd +28 permissions/roles.py
badd +10 test/utils.py
badd +351 apis/work_command_state.py
badd +289 apis/manufacture.py
badd +20 apis/quality_inspection.py
badd +71 templates/work-flow/node-list.html
badd +12 portal/admin/order_settings.py
badd +81 portal/deduction/__init__.py
badd +2 templates/work-flow/permit-delivery-task-with-abnormal-weight-annotation.html
badd +1 templates/admin2/department-leader-list-snippet.html
badd +86 apis/cargo.py
badd +43 ~/work/lite-mms-dev/lite-mms/alembic/versions/43d2714c4448_.py
badd +30 ~/work/lite-mms-dev/lite-mms/alembic/versions/185ce9f63e22_move_deduction.py
badd +51 ~/work/lite-mms-dev/lite-mms/alembic.ini
badd +3 constants/work_flow.py
badd +1 constants/__init__.py
badd +61 ~/work/lite-mms-dev/lite-mms/requirements.txt
badd +1 static/css/customer.css
badd +1 templates/layout.html
badd +201 templates/__data_browser__/layout.html
badd +7 portal/delivery_ws/__init__.py
badd +82 ~/work/lite-mms-dev/lib/python2.7/site-packages/pylint/reporters/text.py
badd +33 constants/cargo.py
badd +8 portal/cargo_ws/__init__.py
badd +45 portal/cargo_ws/webservices.py
badd +168 utilities/decorators.py
badd +44 portal/auth/views.py
badd +375 portal/manufacture_ws/webservices.py
badd +6 portal/order_ws/webservices.py
badd +16 portal/cargo/ajax.py
badd +16 constants/work_command.py
badd +32 test/at/test_cargo.py
badd +6 test/at/test_order.py
badd +90 test/at/test_manufacture.py
badd +197 test/at/steps/manufacture.py
badd +254 portal/manufacture/views.py
badd +117 portal/order/views.py
badd +15 features/then.py
badd +21 portal/manufacture/actions.py
badd +101 portal/manufacture/__init__.py
badd +3 constants/quality_inspection.py
badd +3 constants/delivery.py
badd +1 ~/.vimrc
badd +1113 ~/work/lite-mms-dev/lite-mms/docs/source/webservices.rst
silent! argdel *
edit test/at/steps/manufacture.py
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
exe '1resize ' . ((&lines * 46 + 27) / 55)
exe '2resize ' . ((&lines * 6 + 27) / 55)
argglobal
let s:cpo_save=&cpo
set cpo&vim
inoremap <buffer> <silent> <S-Tab> =RopeLuckyAssistInsertMode()
imap <buffer> <C-Space> ¯
imap <buffer> <Nul> ¯
noremap <buffer> <silent> g :RopeGotoDefinition
noremap <buffer> <silent> d :RopeShowDoc
noremap <buffer> <silent> f :RopeFindOccurrences
noremap <buffer> <silent> m :emenu Rope . 	
nnoremap <buffer> <silent> ,r :Pyrun
vnoremap <buffer> <silent> ,r :Pyrun
nnoremap <buffer> <silent> ,b :call pymode#breakpoint#Set(line('.'))
onoremap <buffer> C :call pymode#motion#select('^\s*class\s', 0)
nnoremap <buffer> <silent> K :call pymode#doc#Show(expand('<cword>'))
vnoremap <buffer> <silent> K :call pymode#doc#Show(@*)
onoremap <buffer> M :call pymode#motion#select('^\s*def\s', 0)
nnoremap <buffer> [[ :call pymode#motion#move('^\(class\|def\)\s', 'b')
nnoremap <buffer> [C :call pymode#motion#move('^\(class\|def\)\s', 'b')
nnoremap <buffer> [M :call pymode#motion#move('^\s*def\s', 'b')
onoremap <buffer> [[ :call pymode#motion#move('^\(class\|def\)\s', 'b')
onoremap <buffer> [C :call pymode#motion#move('^\(class\|def\)\s', 'b')
onoremap <buffer> [M :call pymode#motion#move('^\s*def\s', 'b')
vnoremap <buffer> [[ :call pymode#motion#vmove('^\(class\|def\)\s', 'b')
vnoremap <buffer> [M :call pymode#motion#vmove('^\s*def\s', 'b')
nnoremap <buffer> ]] :call pymode#motion#move('^\(class\|def\)\s', '')
nnoremap <buffer> ]C :call pymode#motion#move('^\(class\|def\)\s', '')
nnoremap <buffer> ]M :call pymode#motion#move('^\s*def\s', '')
onoremap <buffer> ]] :call pymode#motion#move('^\(class\|def\)\s', '')
onoremap <buffer> ]C :call pymode#motion#move('^\(class\|def\)\s', '')
onoremap <buffer> ]M :call pymode#motion#move('^\s*def\s', '')
vnoremap <buffer> ]] :call pymode#motion#vmove('^\(class\|def\)\s', '')
vnoremap <buffer> ]M :call pymode#motion#vmove('^\s*def\s', '')
onoremap <buffer> aC :call pymode#motion#select('^\s*class\s', 0)
vnoremap <buffer> aC :call pymode#motion#select('^\s*class\s', 0)
onoremap <buffer> aM :call pymode#motion#select('^\s*def\s', 0)
vnoremap <buffer> aM :call pymode#motion#select('^\s*def\s', 0)
onoremap <buffer> iC :call pymode#motion#select('^\s*class\s', 1)
vnoremap <buffer> iC :call pymode#motion#select('^\s*class\s', 1)
onoremap <buffer> iM :call pymode#motion#select('^\s*def\s', 1)
vnoremap <buffer> iM :call pymode#motion#select('^\s*def\s', 1)
inoreabbr <buffer> cfun =IMAP_PutTextWithMovement("def <++>(<++>):\n<++>\nreturn <++>")
inoreabbr <buffer> cclass =IMAP_PutTextWithMovement("class <++>:\n<++>")
inoreabbr <buffer> cfor =IMAP_PutTextWithMovement("for <++> in <++>:\n<++>")
inoreabbr <buffer> cif =IMAP_PutTextWithMovement("if <++>:\n<++>")
inoreabbr <buffer> cifelse =IMAP_PutTextWithMovement("if <++>:\n<++>\nelse:\n<++>")
inoreabbr <buffer> ctry =IMAP_PutTextWithMovement("try:\n<++>\nexcept <++>:\n    <++>")
inoreabbr <buffer> cfrom =IMAP_PutTextWithMovement("from <++> import <++>")
let &cpo=s:cpo_save
unlet s:cpo_save
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal balloonexpr=
setlocal nobinary
setlocal bufhidden=
setlocal buflisted
setlocal buftype=
setlocal nocindent
setlocal cinkeys=0{,0},0),:,!^F,o,O,e
setlocal cinoptions=
setlocal cinwords=if,else,while,do,for,switch
set colorcolumn=78
setlocal colorcolumn=78
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:XCOMM,n:>,fb:-
setlocal commentstring=#%s
setlocal complete=.,w,b,u,t,i
setlocal concealcursor=
setlocal conceallevel=0
setlocal completefunc=
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=%+P[%f],%t:\ %#%l:%m,%Z,%+IYour\ code%m,%Z,%-G%.%#
setlocal expandtab
if &filetype != 'python'
setlocal filetype=python
endif
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=pymode#folding#expr(v:lnum)
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
setlocal foldmethod=expr
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=pymode#folding#text()
setlocal formatexpr=
setlocal formatoptions=cqmM
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=2
setlocal imsearch=2
setlocal include=^\\s*\\(from\\|import\\)
setlocal includeexpr=substitute(v:fname,'\\.','/','g')
setlocal indentexpr=pymode#indent#Indent(v:lnum)
setlocal indentkeys=!^F,o,O,<:>,0),0],0},=elif,=except
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=pydoc
setlocal nolinebreak
setlocal nolisp
setlocal nolist
setlocal makeprg=(echo\ '[%]';\ pylint\ -r\ y\ %)
setlocal matchpairs=(:),{:},[:]
setlocal modeline
setlocal modifiable
setlocal nrformats=octal,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=RopeOmni
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norelativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=4
setlocal noshortname
setlocal nosmartindent
setlocal softtabstop=4
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=
setlocal suffixesadd=.py
setlocal swapfile
setlocal synmaxcol=3000
if &syntax != 'python'
setlocal syntax=python
endif
setlocal tabstop=4
setlocal tags=
setlocal textwidth=79
setlocal thesaurus=
setlocal noundofile
setlocal nowinfixheight
setlocal nowinfixwidth
setlocal nowrap
setlocal wrapmargin=0
42
normal zo
74
normal zo
142
normal zo
170
normal zo
174
normal zo
181
normal zo
182
normal zo
199
normal zo
200
normal zo
let s:l = 155 - ((8 * winheight(0) + 23) / 46)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
155
normal! 024l
lcd ~/work/lite-mms-dev/lite-mms/lite_mms
wincmd w
argglobal
enew
setlocal keymap=
setlocal noarabic
setlocal autoindent
setlocal balloonexpr=
setlocal nobinary
setlocal bufhidden=wipe
setlocal buflisted
setlocal buftype=quickfix
setlocal nocindent
setlocal cinkeys=0{,0},0),:,0#,!^F,o,O,e
setlocal cinoptions=
setlocal cinwords=if,else,while,do,for,switch
set colorcolumn=78
setlocal colorcolumn=78
setlocal comments=s1:/*,mb:*,ex:*/,://,b:#,:%,:XCOMM,n:>,fb:-
setlocal commentstring=/*%s*/
setlocal complete=.,w,b,u,t,i
setlocal concealcursor=
setlocal conceallevel=0
setlocal completefunc=
setlocal nocopyindent
setlocal cryptmethod=
setlocal nocursorbind
setlocal nocursorcolumn
setlocal nocursorline
setlocal define=
setlocal dictionary=
setlocal nodiff
setlocal equalprg=
setlocal errorformat=
setlocal expandtab
if &filetype != 'qf'
setlocal filetype=qf
endif
setlocal foldcolumn=0
setlocal foldenable
setlocal foldexpr=0
setlocal foldignore=#
setlocal foldlevel=0
setlocal foldmarker={{{,}}}
setlocal foldmethod=manual
setlocal foldminlines=1
setlocal foldnestmax=20
setlocal foldtext=foldtext()
setlocal formatexpr=
setlocal formatoptions=tcqmM
setlocal formatlistpat=^\\s*\\d\\+[\\]:.)}\\t\ ]\\s*
setlocal grepprg=
setlocal iminsert=2
setlocal imsearch=2
setlocal include=
setlocal includeexpr=
setlocal indentexpr=
setlocal indentkeys=0{,0},:,0#,!^F,o,O,e
setlocal noinfercase
setlocal iskeyword=@,48-57,_,192-255
setlocal keywordprg=
setlocal nolinebreak
setlocal nolisp
setlocal nolist
setlocal makeprg=
setlocal matchpairs=(:),{:},[:]
setlocal modeline
setlocal nomodifiable
setlocal nrformats=octal,hex
set number
setlocal number
setlocal numberwidth=4
setlocal omnifunc=
setlocal path=
setlocal nopreserveindent
setlocal nopreviewwindow
setlocal quoteescape=\\
setlocal noreadonly
setlocal norelativenumber
setlocal norightleft
setlocal rightleftcmd=search
setlocal noscrollbind
setlocal shiftwidth=4
setlocal noshortname
setlocal nosmartindent
setlocal softtabstop=0
setlocal nospell
setlocal spellcapcheck=[.?!]\\_[\\])'\"\	\ ]\\+
setlocal spellfile=
setlocal spelllang=en
setlocal statusline=%t%{exists('w:quickfix_title')?\ '\ '.w:quickfix_title\ :\ ''}\ %=%-15(%l,%c%V%)\ %P
setlocal suffixesadd=
setlocal noswapfile
setlocal synmaxcol=3000
if &syntax != 'qf'
setlocal syntax=qf
endif
setlocal tabstop=4
setlocal tags=
setlocal textwidth=0
setlocal thesaurus=
setlocal noundofile
setlocal winfixheight
setlocal nowinfixwidth
setlocal wrap
setlocal wrapmargin=0
lcd ~/work/lite-mms-dev/lite-mms/lite_mms
wincmd w
exe '1resize ' . ((&lines * 46 + 27) / 55)
exe '2resize ' . ((&lines * 6 + 27) / 55)
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
