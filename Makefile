all: clean test www

upload: docker_upload

docker: docker_build docker_run

build: build_prod push_prod

clean: clean_build

test: pep8 test_django jslint

django_db: db

DOCKER_TAG = servercobra/triviastats
#########################
# Dev tools
#########################

docker_upload:
	docker build -t $(DOCKER_TAG):testing .
	docker push $(DOCKER_TAG):testing

pep8:
	tox -epep8

test_django:
	tox -edjango

db:
	python manage.py syncdb
	python manage.py migrate

# Load dev data
load_data:
	python manage.py loaddata scores.fixture

#########################
# Build/deploy tools
#########################

jslint:
	cd frontend && gulp lint

prod:
	cd frontend && gulp build
	cd frontend && gulp prod

preprod:
	cd frontend && gulp build
	cd frontend && gulp preprod

clean_build:
	cd frontend && gulp clean

#########################
# CI/CD tools
#########################

install_ci:
	cd frontend && npm install -g bower gulp

build_testing:
	docker build -t $(DOCKER_TAG):testing .

push_testing:
	docker push $(DOCKER_TAG):testing

build_prod:
	docker build -t $(DOCKER_TAG) .

push_prod:
	docker push $(DOCKER_TAG)

docker_run:
	docker run -i -v `pwd`:/home/docker/code -p 80:80 -t $(DOCKER_TAG)

#########################
# Misc
#########################

whoopee:
	echo "Sorry, I'm not in the mood"
