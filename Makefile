DOCKER_IMAGE=societhy/localenv
TEST_IMAGE=societhy/tests

all:
	@make build
	@make shell

test:
	@make build_test
	@make local_test

build_dependencies:
	npm --prefix ./app/web install ./app/web
	bower install ./app/web

build:
	docker build -t $(DOCKER_IMAGE) .

build_test:
	docker build --file Dockerfile_tests -t $(TEST_IMAGE) .
	
local_test:
	docker-compose -f utils/docker-compose.yaml up -d test_remote_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/tests | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/tests | cut -f 1 -d " "` pytest -svv tests/'
	sh -c "docker stop `docker ps | grep societhy/tests | cut -f 1 -d " "`"

prod:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sh -c 'docker exec -t -i `docker ps | grep societhy/localenv | cut -f 1 -d " "` scp -r exploit@163.5.84.117:/home/exploit/.parity/keys /societhy/.parity/keys'
	sh -c 'docker exec -t -i `docker ps | grep societhy/localenv | cut -f 1 -d " "` /bin/zsh'

shell:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sh -c 'docker exec -t -i `docker ps | grep societhy/localenv | cut -f 1 -d " "` /bin/zsh'
	@make stop

mine:
	docker-compose -f utils/docker-compose.yaml up -d test_local_mining_env
	sh -c 'docker exec -t -i `docker ps | grep societhy/localenv | cut -f 1 -d " "` /bin/zsh'
	@make stop

stop:
	sh -c 'docker stop `docker ps -a -q`'	

rmall:
	@make stop
	sh -c 'docker rm `docker ps -a -q`'