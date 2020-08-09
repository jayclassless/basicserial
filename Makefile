
setup::
	@poetry install

env::
	@poetry self --version
	@poetry version
	@poetry env info
	@poetry show --all

clean::
	@rm -rf dist .coverage poetry.lock

clean-full:: clean
	@poetry env remove `poetry run which python`

test::
	@poetry run coverage run --module py.test
	@poetry run coverage report

build::
	@poetry build

publish::
	@poetry publish

