# clip API

API Wrapper of the `clip-vit-base-patch32` model to generate image embeddings at scale


## Usage
There are a few testing endpoints
* GET localhost:5000/ping    [alive endpoint]
* GET localhost:5000/smoke   [generate embedding for 1 locally stored image]
* GET localhost:5000/smoke10 [generate embedding for 10 locally stored images]

To process single image
* GET localhost:5000/image?img_url={image_url}

To process multiple images
* POST localhost:5000/images
```
{"images": [
"image_url_1",
"image_url_2"
]}
```


## Develop
```
pip install -r requirements.txt

python -m flask run --host=0.0.0.0
```



## Deploy
```
docker run --name clip -d \
  --restart unless-stopped \
  nojson/clip-api:20240401.1
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
  nojson/clip-api:20240401.1
```

### Run Flask using customized parameter
`python3 -m flask run --host=0.0.0.0 --port 80`
Example:
```
docker run --name clip -d \
  --restart unless-stopped \
  --network host \
  nojson/clip-api:20240401.1 python3 -m flask run --host=0.0.0.0 --port 80
```

## Considerations
Do not use Gunicorn or UWSGI, as typical multi-threading deployment tooling designed for typical APIs does not produce optimal throughput when using a large model per process initiation.
