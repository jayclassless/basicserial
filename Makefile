VENV = .venv
BINDIR = $(if $(wildcard ${VENV}/bin), '${VENV}/bin/', '')


setup::
	@python -m venv ${VENV}
	@${MAKE} install

setup-ci:: install

install::
	@${BINDIR}pip install --upgrade pip
	@${BINDIR}pip install -r requirements.txt
	@${BINDIR}pip install -e .

freeze::
	@${BINDIR}python --version
	@${BINDIR}pip --version
	@${BINDIR}pip freeze

clean::
	@rm -rf dist build .cache .pytest_cache pip-wheel-metadata .coverage.*

clean-full:: clean
	@rm -rf .venv


test::
	@${BINDIR}coverage run --rcfile=setup.cfg --module py.test
	@${BINDIR}coverage report --rcfile=setup.cfg

test-ci:: test


build:: clean
	@${BINDIR}python setup.py sdist
	@${BINDIR}python setup.py bdist_wheel

publish::
	@${BINDIR}twine upload dist/*

