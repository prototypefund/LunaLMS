help:
	@echo targets:
	@echo '    check'
	@echo '    errors'
	@echo '    sdist'
	@echo '    docs'
#	@echo '    exe'
#	@echo '    user_install'
	@echo '    clean'
	@echo '    commit.txt'
	@echo '    commit'

check:
	pylint luna_lms

errors:
	pylint --errors-only luna_lms

ifdef PYTHON

sdist:
	rm -vf MANIFEST
	$(PYTHON) setup.py sdist --formats=zip

#exe: sdist
#	rm -rf build/exe.*
#	$(PYTHON) setup.py build

#user_install:
#	$(PYTHON) setup.py install --user --record user_install-filelist.txt

else

sdist:
	@echo Please supply Python executable as PYTHON=executable.

#exe:
#	@echo Please supply Python executable as PYTHON=executable.

#user_install:
#	@echo Please supply Python executable as PYTHON=executable.

endif

docs: clean
	pydoctor --verbose \
		--docformat plaintext \
		--make-html \
		--html-output dokumentation/api/ \
		luna_lms

clean:
	@echo About to remove all log files. RETURN to proceed && read DUMMY && rm -vf `find . -iname '*.log'`
	rm -rvf `find . -type d -iname '__pycache__'`
	rm -vf `find . -iname '*.pyc'`
	rm -vf `find . -iname '*~'`

commit.txt:
	fossil diff > commit.txt

commit: commit.txt
	@echo commit.txt:
	@echo ------------------------------------------------------
	@cat commit.txt
	@echo ------------------------------------------------------
	@echo RETURN to commit using commit.txt, CTRL-C to cancel:
	@read DUMMY
	fossil commit --message-file commit.txt && rm -v commit.txt
