DOCKER_IMAGE=societhy/env

all:
	@make build
	@make shell

test:
	@make build
	@make local_test

build_dependencies:
	npm --prefix ./app/web install ./app/web
	bower install ./app/web

build:
	docker build -t $(DOCKER_IMAGE) .

force_build:
	docker build --no-cache -t $(DOCKER_IMAGE) .

local_test:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` pytest -svv tests/'
	sh -c "docker stop `docker ps | grep societhy/env | cut -f 1 -d " "`"

prod:
	docker-compose -f utils/docker-compose.yaml up -d test_prod_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` ps -eaf'
	#sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` scp -r exploit@163.5.84.117:/home/exploit/.parity/keys /societhy/.parity/keys'
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` /bin/zsh'
	@make stop

shell:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/env | cut -f 1 -d " "` /bin/zsh'
	@make stop

stop:
	sh -c 'docker stop `docker ps -a -q`'	

rmall:
	@make stop
	sh -c 'docker rm `docker ps -a -q`'