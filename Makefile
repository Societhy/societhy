DOCKER_IMAGE=societhy/localenv

all:
	@make build
	@make shell

build_dependencies:
	npm --prefix ./app/web install ./app/web
	bower install ./app/web

build:
	docker build -t $(DOCKER_IMAGE) .


shell:
	docker-compose -f utils/docker-compose.yaml up -d testenv
	sh -c 'docker exec -t -i `docker ps | grep societhy/localenv | cut -f 1 -d " "` /bin/bash'

rmall:
	sh -c 'docker stop `docker ps -a -q`'
	sh -c 'docker rm `docker ps -a -q`'
