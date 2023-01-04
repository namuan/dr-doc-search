export PROJECTNAME=$(shell basename "$(PWD)")

.SILENT: ;               # no need for @

new-project: ## Instruction to setup a new project. Run ./init-new-project.sh NEW_PROJECT_NAME
	echo "Run ./init-new-project.sh NEW_PROJECT_NAME"

setup: ## Setup Virtual Env
	poetry install

deps: ## Install/Update dependencies
	poetry lock
	poetry run pre-commit autoupdate

local: ## Locally install the package
	poetry install
	dr-doc-search --help

clean: ## Clean package
	find . -type d -name '__pycache__' | xargs rm -rf
	find . -type d -name '.temp' | xargs rm -rf
	find . -type f -name '.coverage' | xargs rm -rf
	rm -rf build dist

comby: ## Generic rules (required comby https://comby.dev/docs/)
	comby 'print(:[1])' 'logging.info(:[1])' -directory 'src' -extensions 'py' -in-place

pre-commit: ## Manually run all precommit hooks
	poetry run pre-commit run --all-files

pre-commit-tool: ## Manually run a single pre-commit hook
	poetry run pre-commit run $(TOOL) --all-files

add: ## Adds a package with poetry - Use make deps to update packages
	poetry add $(PACKAGE)

add-dev: ## Adds a dev package with poetry - Use make deps to update packages
	poetry add --group dev $(PACKAGE)

tests: clean ## Run all tests
	poetry run pytest
	poetry run coverage xml -i

build: pre-commit tests ## Build package
	poetry build

bump: build ## Bump version and update changelog
	poetry run cz bump --changelog

bpython: ## Runs bpython
	bpython

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo
