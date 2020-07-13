hooksPath := $(git config --get core.hooksPath)

.PHONY: precommit
default: precommit

precommit:
ifneq ($(strip $(hooksPath)),.github/hooks)
	@git config --add core.hooksPath .github/hooks
endif

lint:
	autopep8 --in-place --aggressive --max-line-length 120 -r .
	black .

install:
	pip3 install --user -r requirements.txt
	pip3 install --user -v -e .

uninstall:
	# TODO why doesn't this cleanup scripts
	pip3 uninstall github-copy -y
	rm -f ~/.local/bin/github_copy.py
	rm -f ~/.local/bin/action.py
	rm -f ~/.local/bin/prefix.py
#	sudo python3 setup.py install --record uninstall-files.txt
#	sudo xargs rm -rf < uninstall-files.txt
#	cat uninstall-files.txt
#	rm -f uninstall-files.txt

reinstall: uninstall install

bundle:
	pip3 download -r requirements.txt -d dependencies
	mkdir bundle
	tar czf /tmp/github-copy.tar.gz .
	mv /tmp/github-copy.tar.gz bundle/github-copy.tar.gz

clean:
	rm -rf dependencies/
	rm -rf bundle/
	rm -rf build/
