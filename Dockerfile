FROM python:3.6

ENV ENV=prod
ENV INTERNAL_GRAFANA_HOST=panel_service_grafana
ENV INTERNAL_GRAFANA_PORT=3000
ENV EXTERNAL_GRAFANA_URL=https://panel-service.hesi.energy/grafana

# Install Python dependencies.
COPY requirements.txt /code/

WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt

# Only now copy the code into the container. Everything before this will be cached
# even with code changes.
COPY . /code
RUN pip install -e .

CMD ["gunicorn", "influxdbgraphs.api.main:app", "-t 5", "-w 1", "-b :5000"]
