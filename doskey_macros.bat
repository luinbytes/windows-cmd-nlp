@echo off
REM DOSKEY macros for Windows CMD NLP Parser
REM This file is loaded automatically via AutoRun when CMD starts
REM It creates aliases so you can type natural language without the 'nlp' prefix

REM Only set up if nlp command is available
where nlp >nul 2>nul
if errorlevel 1 exit /b 0

REM Common navigation shortcuts
DOSKEY ls=nlp list files $*
DOSKEY ll=nlp list files detailed $*
DOSKEY dir=nlp list files $*

REM Navigation without typing 'go to'
DOSKEY go=nlp go to $*
DOSKEY cd=nlp go to $*
DOSKEY back=nlp go back
DOSKEY up=nlp go up
DOSKEY home=nlp go home

REM File operations
DOSKEY find=nlp find files $*
DOSKEY create=nlp create $*
DOSKEY make=nlp create $*
DOSKEY delete=nlp delete $*
DOSKEY remove=nlp delete $*
DOSKEY copy=nlp copy $*
DOSKEY move=nlp move $*
DOSKEY rename=nlp rename $*

REM System commands
DOSKEY show=nlp show $*
DOSKEY open=nlp open $*
DOSKEY run=nlp run $*
DOSKEY kill=nlp kill $*
DOSKEY clear=nlp clear

REM Git shortcuts
DOSKEY status=nlp git status
DOSKEY commit=nlp git commit $*
DOSKEY push=nlp git push $*
DOSKEY pull=nlp git pull $*
DOSKEY branch=nlp git branch $*

REM Help
DOSKEY help=nlp --help
DOSKEY ? = nlp --help

REM The magic catch-all: if typed text isn't a known command, try nlp
REM Note: This requires more complex setup via doskey_install.bat