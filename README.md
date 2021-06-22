# Panel Service

This API allows users to easily create graphs in Grafana for InfluxDB data, by providing queries and other parameters.

## Getting started

The code runs in Docker, so as prerequisites you will need to install both Docker and docker-compose.

To start developing, first build all necessary code:

```bash
make
```

And then run all services locally:

```bash
make dev
```

Next to the API, this will also start a Grafana, InfluxDB and Chronograf instance. You probably won't need the latter much, but it's there for any backend administration into InfluxDB.

## Production

Deployment has to be done to a docker swarm. Before the panel service can be deployed, it needs an API key for Grafana. First deploy Grafana:

```bash
make network
make deploy-grafana
```

Then, head over to port 3301 on the localhost and sign in. The default username and password is
admin.

Under configuration (the cogwheel on the left), go to API Keys, and click on New API Key. Create a
key with role Admin. As name, fill out panelservice.

Then, create a local file called panel_service.env, and set `GRAFANA_API_KEY=<API_KEY>`.

Please follow the following procedure to deploy the panel service:

```bash
make build
make tag
make publish
make deploy
```

This will build the panel service, tag the image, push it to the local registry, and deploys it (and
the Grafana service) to the Docker Swarm.

The same commands are also available through the package.json (executed through `npm run <command>`).

To stop, execute:

```bash
make remove
```

## Examples

### Full example of creating panel

POST to /graphs/

```json
{
    "title": "Test Dashboard",
    "start": "2010-01-01T00:00:00.000+0100",
    "end": "2011-01-01T01:00:00.000+0100",
    "influxdb_name": "EDR-profiles",
    "raw_influx_queries": [
        {
        	"query": "SELECT mean(\"E2A\") FROM \"autogen\".\"nedu_elektriciteit_2010-2014\" WHERE $timeFilter GROUP BY time($__interval) fill(null)",
            "alias": "E2A"
        }
    ],
    "influx_queries": [
        {
            "measurement": "nedu_elektriciteit_2010-2014",
            "field": "E1A",
            "function": "sum",
            "alias": "E1A",
            "filters": [
		    	"E1A < 5"
		    ],
            "yaxis": "right",
		    "group_by_time": "$__interval",
            "fill": "null"
        }
    ],
    "yaxes": [{
    	"format": "litre"
    }, {
    	"format": "watth",
    	"min": null
    }],
    "thresholds": [
    	{
    		"value": 0.00003,
    		"op": "gt"
    	}
    ],
    "theme": "light",
    "grafana_graph_params": {
    	"lineWidth": 1
    }
}
```

### Create data source

POST to /influxdbs/

```json
{
	"name": "EDRProfileDB",
	"url": "https://edr.hesi.energy/profiledb",
	"database_name": "energy_profiles",
	"basic_auth_user": "username",
	"basic_auth_password": "password"
}
```

### Create query and refer to influxdb by URL.

POST to /graphs/

```json
{
    "title": "Elektriciteit huishoudens 2015 (NEDU E1A)",
    "start": "2015-01-01T00:00:00.000+0100",
    "end": "2016-01-01T00:00:00.000+0100",
    "influxdb": {
        "url": "https://edr.hesi.energy/profiledb",
        "database": "energy_profiles"
    },
    "influx_queries": [
        {
            "measurement": "nedu_elektriciteit_2015-2018",
            "field": "E1A",
            "alias": "E1A"
        }
    ],
    "theme": "light"
}
```
