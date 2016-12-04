DOCKER_IMAGE=societhy/localenv
TEST_IMAGE=societhy/tests

all:
	@make build
	@make shell

build_dependencies:
	npm --prefix ./app/web install ./app/web
	bower install ./app/web

test:
	docker build --file Dockerfile_tests -t $(TEST_IMAGE) .
	docker-compose -f utils/docker-compose.yaml up -d test_remote_env
	sh -c 'docker exec -t -i `docker ps | grep societhy/tests | cut -f 1 -d " "` pytest tests/'

build:
	docker build -t $(DOCKER_IMAGE) .

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