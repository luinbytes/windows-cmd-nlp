@echo off
REM Windows CMD NLP Parser wrapper
REM Usage: nlp "your command here"
REM      nlp --interactive
REM      nlp --help

python "%~dp0cmd_nlp.py" %*
