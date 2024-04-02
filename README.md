# clip API

API Wrapper of the `clip-vit-base-patch32` model to generate image embeddings at scale


## Usage
There are a few testing endpoints
* GET localhost:5000/ping    [alive endpoint]
* GET localhost:5000/smoke   [generate embedding for 1 locally stored image]
* GET localhost:5000/smoke10 [generate embedding for 10 locally stored images]

#### Embedding for single image
* GET localhost:5000/image?img_url={image_url}

#### Embedding for multiple images
* POST localhost:5000/images
```
{"images": [
"image_url_1",
"image_url_2"
]}
```

#### Image to Image similarity score
* GET localhost:5003/image-image?img_url1={image_url1}&img_url2={image_url2}

```
http://localhost:5000/image-image?img_url1=https://www.alleycat.org/wp-content/uploads/2019/03/FELV-cat.jpg&img_url2=https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1280px-Cat03.jpg
```


#### Image to Text similarity score
* GET localhost:5000/image-text?text={text with | as delim, space is allowed}&img_url={image_url}
Example of text: `festival|evening|frog|water bottle|shirt|pants`

```
http://localhost:5000/image-text?text=dog|cat|frog|water bottle|shirt|pants&img_url=https://cdn.shopify.com/s/files/1/0277/9519/3890/files/436-4367467_dog-cat-cute-animal-stickers-labs-and-cats_480x480.png
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
  nojson/clip-api:20240402.1
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
  nojson/clip-api:20240402.1
```

### Run Flask using customized parameter
`python3 -m flask run --host=0.0.0.0 --port 80`
Example:
```
docker run --name clip -d \
  --restart unless-stopped \
  --network host \
  nojson/clip-api:20240402.1 python3 -m flask run --host=0.0.0.0 --port 80
```

## Considerations
Do not use Gunicorn or UWSGI, as typical multi-threading deployment tooling designed for typical APIs does not produce optimal throughput when using a large model per process initiation.
