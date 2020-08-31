all:
	docker-compose build api

build-no-cache:
	docker-compose build --no-cache api

dev:
	docker-compose up

down:
	docker-compose down


# Deployment commands.

build:
	docker build -t panel-service .
tag:
	docker tag panel-service 127.0.0.1:5000/panel-service
publish:
	docker push 127.0.0.1:5000/panel-service
network:
	docker network create --driver overlay panel-service
deploy:
	docker service create --name panel-service -p 3300:5000 --network panel-service --env-file panel-service.env 127.0.0.1:5000/panel-service
remove:
	docker service rm panel-service | true

deploy-grafana:
	docker service create \
	    --name panel-service-grafana \
	    -p 3301:3000 \
	    --constraint "node.labels.panel-service.grafana == true" \
	    --network panel-service \
	    --env-file grafana.env \
	    --mount src=grafana-panel-service-data,dst=/var/lib/grafana grafana/grafana:6.5.1
remove-grafana:
	docker service rm panel-service-grafana | true

remove-network:
	docker network rm panel-service | true

docker: build tag publish remove deploy
docker-full: build tag publish remove remove-grafana remove-network network deploy-grafana deploy
