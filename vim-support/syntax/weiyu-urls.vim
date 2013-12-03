" Vim syntax file
" Language:	weiyu Routing Language
" Maintainer:	Wang Xuerui <idontknw.wang@gmail.com>
" Last Change:	2013 Dec 03
" Version:      0.1
"
" Basic structure of this file is borrowed from python.vim.

if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif


" Extras are JSON literals, but Vim only has JavaScript syntax file...
syn include @jsTop syntax/javascript.vim


" LINECOMMENT
syn match wyURLComment "#.*$" contains=wyURLTodo,@Spell
syn keyword wyURLTodo contained FIXME NOTE NOTES TODO XXX


" ATTRIB
syn match wyURLAttrib /^\s*\zs--.*$/
    \ contains=wyURLAttribKey,wyURLAttribEquals,wyURLAttribRouterClass

syn match wyURLAttribKey contained /include=/
    \ nextgroup=wyURLAttribValue
syn match wyURLAttribKey contained /renderer=/
    \ nextgroup=@wyURLRenderer
syn match wyURLAttribKey contained /scope=/
    \ nextgroup=wyURLAttribValue

syn match wyURLAttribValue contained /.*/

syn match wyURLAttribRouterClass contained /regex/
syn match wyURLAttribRouterClass contained /exact/


" Extras in JSON
syn match wyURLExtras /.*/ contained transparent
    \ contains=@jsTop


" Renderers
syn keyword wyURLRendererKeywords null inherit
    \ nextgroup=wyURLExtras
syn keyword wyURLRendererBuiltin mako json scss dummy
    \ nextgroup=wyURLExtras
syn cluster wyURLRenderer
    \ contains=wyURLRendererKeyword,wyURLRendererBuiltin


" Router spec
syn match wyURLColon /:/ contained

syn match wyURLPattern /^\s*\zs[^#'" \t-]*[^#'" \t:-]/
    \ contains=@wyURLPatternGroups,@wyURLPatternExprs
    \ nextgroup=wyURLColon,wyURLEndpoint skipwhite
syn match wyURLPattern /^\s*\zs[^#'" \t-][^#'" \t]*[^#'" \t:-]/
    \ contains=@wyURLPatternGroups,@wyURLPatternExprs
    \ nextgroup=wyURLColon,wyURLEndpoint skipwhite
syn region wyURLPattern start=/^\s*\zs\'/ end=/\'/
    \ contains=@wyURLPatternGroups,@wyURLPatternExprs
    \ nextgroup=wyURLColon,wyURLEndpoint skipwhite
syn region wyURLPattern start=/^\s*\zs\"/ end=/\"/
    \ contains=@wyURLPatternGroups,@wyURLPatternExprs
    \ nextgroup=wyURLColon,wyURLEndpoint skipwhite

syn match wyURLEndpoint /[^ \t:][^ \t]*/ contained
    \ nextgroup=@wyURLRenderer skipwhite


" Highlighting of interesting RE patterns
" Clusters are implicitly declared in pattern rules above and below.
" Groups
syn region wyURLPatternNamedGroup start=/(?P/ end=/)/ contained
    \ contains=wyURLPatternGroupName,@wyURLPatternGroups,@wyURLPatternExprs
syn match wyURLPatternGroupName /\((?P\)\@3<=[<][^()<>]*[>]/ contained
syn cluster wyURLPatternGroups
    \ add=wyURLPatternNamedGroup

syn region wyURLPatternNonCapturingGroup start=/(?:/ end=/)/ contained
    \ contains=@wyURLPatternGroups,@wyURLPatternExprs
syn cluster wyURLPatternGroups
    \ add=wyURLPatternNonCapturingGroup


" Expressions
syn match wyURLPatternEscapes /\\A\|\\a\|\\B\|\\b\|\\D\|\\d\|\\f\|\\n\|\\r\|\\S\|\\s\|\\t\|\\v\|\\W\|\\w\|\\x\|\\Z\|\\\\/ contained
syn match wyURLPatternEscapes /\\\*\|\\+\|\\?\|\\\.\|\\\^\|\\\$\|\\|\|\\(\|\\)\|\\\[\|\\\]\|\\{\|\\}/ contained
syn cluster wyURLPatternExprs
    \ add=wyURLPatternEscapes

syn match wyURLPatternExtremes /\^\|\$/ contained
syn cluster wyURLPatternExprs
    \ add=wyURLPatternExtremes

syn match wyURLPatternAlternatives /|/ contained
syn cluster wyURLPatternExprs
    \ add=wyURLPatternAlternatives

syn region wyURLPatternCharClass matchgroup=wyURLPatternCharClassBrackets start=/\[/ end=/\]/ contained
syn region wyURLPatternCharClass matchgroup=wyURLPatternCharClassBrackets start=/\[\^/ end=/\]/ contained
syn cluster wyURLPatternExprs
    \ add=wyURLPatternCharClass

"syn match wyURLPatternRepetitions /[\*]\@1<!\\/ contained
syn match wyURLPatternRepetitions /\*\|+/ contained
syn match wyURLPatternRepetitions /\((\)\@1<!?/ contained
syn match wyURLPatternRepetitions /{\d\+}/ contained
syn match wyURLPatternRepetitions /{\d\+,}/ contained
syn match wyURLPatternRepetitions /{,\d\+}/ contained
syn match wyURLPatternRepetitions /{\d\+,\d\+}/ contained
syn cluster wyURLPatternExprs
    \ add=wyURLPatternRepetitions


"" trailing whitespace
"syn match   wyURLSpaceError	display excludenl \"\s\+$"
"" mixed tabs and spaces
"syn match   wyURLSpaceError	display \" \+\t"
"syn match   wyURLSpaceError	display \"\t\+ "


" Sync at the beginning of a router definition.
syn sync match wyURLSync grouphere NONE "^[^#]*:"


if version >= 508 || !exists("did_weiyu_urls_syn_inits")
  if version <= 508
    let did_weiyu_urls_syn_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif

  HiLink wyURLComment Comment
  HiLink wyURLTodo Todo

  HiLink wyURLAttrib Operator
  HiLink wyURLAttribKey Define
  HiLink wyURLAttribValue String
  HiLink wyURLAttribRouterClass Type

  HiLink wyURLColon Comment
  HiLink wyURLPattern String
  HiLink wyURLEndpoint Identifier

  HiLink wyURLRendererKeywords Statement
  HiLink wyURLRendererBuiltin Type

  HiLink wyURLPatternExtremes Comment
  HiLink wyURLPatternAlternatives Operator
  HiLink wyURLPatternEscapes Special
  HiLink wyURLPatternRepetitions Operator

  HiLink wyURLPatternCharClass String
  HiLink wyURLPatternCharClassBrackets Comment

  HiLink wyURLPatternNamedGroup Underlined
  HiLink wyURLPatternGroupName Define
  HiLink wyURLPatternNonCapturingGroup Normal

  HiLink wyURLSpaceError Error

  delcommand HiLink
endif

let b:current_syntax = "weiyu-urls"


" vim:set et ts=2 sw=2 sts=2 fenc=utf-8:
