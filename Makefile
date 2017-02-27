DOCKER_IMAGE=societhy/devserver

all:
	@make pull
	@make shell

test:
	@make pull
	@make local_test

pow:
	@make build
	@make pow_test

build_dependencies:
	npm --prefix ./app/web install ./app/web
	bower install --allow-root ./app/web

build:
	docker build -t $(DOCKER_IMAGE) .

force_build:
	docker build --no-cache -t $(DOCKER_IMAGE) .

pull:
	docker pull $(DOCKER_IMAGE)

pow_test:
	docker-compose -f utils/docker-compose.yaml up -d test_pow_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` pytest -svv tests/'
	sh -c "docker stop `docker ps | grep societhy/devserver | cut -f 1 -d " "`"

local_test:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` pytest -svv tests/'
	sh -c "docker stop `docker ps | grep societhy/devserver | cut -f 1 -d " "`"

prod:
	docker-compose -f utils/docker-compose.yaml up -d test_prod_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` ps -eaf'
	#sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` scp -r exploit@163.5.84.117:/home/exploit/.parity/keys /societhy/.parity/keys'
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` /bin/zsh'
	@make stop

shell:
	docker-compose -f utils/docker-compose.yaml up -d test_local_env
	sleep 3
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` ps -eaf'
	sh -c 'docker exec -t -i `docker ps | grep societhy/devserver | cut -f 1 -d " "` /bin/zsh'
	@make stop

stop:
	sh -c 'docker stop `docker ps -a -q`'	

rmall:
	@make stop
	sh -c 'docker rm `docker ps -a -q`'
