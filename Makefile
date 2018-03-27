WITH_ENV = env `cat .env 2>/dev/null | xargs`

compile-deps:
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 install -U pip-tools
	@$(WITH_ENV) pip-compile -U requirements.in
	@$(WITH_ENV) pip-compile -U test-requirements.in

install-deps:
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -r test-requirements.txt
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -r requirements.txt
