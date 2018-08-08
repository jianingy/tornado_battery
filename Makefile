WITH_ENV = env `cat .env 2>/dev/null | xargs`

compile-deps:
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 install -U pip-tools
	@$(WITH_ENV) pip-compile --no-index --no-emit-trusted-host -U requirements.in
	@$(WITH_ENV) pip-compile --no-index --no-emit-trusted-host -U requirements.in requirements-test.in  --output-file=requirements-dev.txt

install-deps:
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -U pip setuptools wheel
	@$(WITH_ENV) pip3 --default-timeout=100 --retries=5 install -r requirements-dev.txt

clean:
	@rm -f dist/*
	@find . -name '*.pyc' -or -name '*.pyo' -or -name '__pycache__' -type f -delete
	@find . -type d -empty -delete

lint:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) flake8

test:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@$(WITH_ENV) tox

dist: clean
	@python3 ./setup.py sdist bdist_wheel

