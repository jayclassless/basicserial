setup::
	@pipenv install --dev --skip-lock

#lint::
#	@pipenv run tidypy check

test::
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage report --rcfile=setup.cfg

ci:: test
	@pipenv run coveralls --rcfile=setup.cfg

clean::
	@rm -rf dist build .cache .pytest_cache .coverage Pipfile.lock pip-wheel-metadata

build:: clean
	@pipenv run python setup.py sdist
	@pipenv run python setup.py bdist_wheel

publish::
	@pipenv run twine upload dist/*

