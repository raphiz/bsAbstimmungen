.PHONY: default
default: buildimage dev

.PHONY: buildimage
buildimage:
	docker build -t raphiz/bs_abstimmungen ./

# This is an alias for the dev container...
within_docker = docker run --rm -it --name bs_abstimmungen -p 8080:8080 -u user -v $(shell pwd):/src/ -e "GIT_AUTHOR_NAME=$(shell git config user.name)" -e "GIT_COMMITTER_NAME=$(shell git config user.name)" -e "EMAIL=$(shell git config user.email)" raphiz/bs_abstimmungen

.PHONY: release
release:
	@echo "Is everything commited? Are you ready to release? Press any key to continue - abort with Ctrl+C"
	@read x
	@$(within_docker) bumpversion --message "Release version {current_version}" --no-commit release
	@$(within_docker) python setup.py sdist bdist_wheel
	@$(within_docker) bumpversion --message "Preparing next version {new_version}" --no-tag patch
	@echo "Don't forget to push the tags (git push origin master --tags)!"

.PHONY: dev
dev:
	@$(within_docker) bash

.PHONY: integration
integration:
	@docker run --rm -it -v $(shell pwd):/src/:ro -w /src python:3.4 bash
