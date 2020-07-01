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