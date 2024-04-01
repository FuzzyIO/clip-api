# clip API

API Wrapper of the `clip-vit-base-patch32` model to generate image embeddings at scale

## Develop
```
pip install -r requirements.txt

python -m flask run --host=0.0.0.0
```
## Deploy
```
docker run --name clip -d \
  --restart unless-stopped \
  nojson/clip-api:20240331.2
```
### Map to host network (for GCP VM's)
`--network host \`

### Chage the exposed port
`-p 80:5000 \`
Example:
```
docker run --name clip -d \
  --restart unless-stopped \
  -p 80:5000 \
  nojson/clip-api:20240331.2
```

### Run Flask using customized parameter
`python3 -m flask run --host=0.0.0.0 --port 80`
Example:
```
docker run --name clip -d \
  --restart unless-stopped \
  --network host \
  nojson/clip-api:20240331.2 python3 -m flask run --host=0.0.0.0 --port 80
```

## Considerations
Do not use Gunicorn or UWSGI, as typical multi-threading deployment tooling designed for typical APIs does not produce optimal throughput when using a large model per process initiation.
