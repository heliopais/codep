.PHONY: all install uninstall test

all: install

install:
	@chmod +x install.sh uninstall.sh bin/codep src/resolver.py
	@./install.sh

uninstall:
	@chmod +x uninstall.sh
	@./uninstall.sh

test:
	@python3 tests/test_resolver.py
