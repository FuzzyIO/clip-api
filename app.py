import torch
from PIL import Image
import requests
import time
import sys
from os import environ as env
from flask import Flask, request, jsonify
import json
from transformers import (
    CLIPProcessor,
    CLIPModel,
)
import logging

LOG_LEVEL = env.get('LOG_LEVEL', 'INFO').upper()
LOCAL_MODEL_DIR = '/opt/models/clip-vit-base-patch32/'

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=LOG_LEVEL,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

logger.warning("STARTING APP")
start_time = time.time()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained(LOCAL_MODEL_DIR)
model.to(device)
processor = CLIPProcessor.from_pretrained(LOCAL_MODEL_DIR)

logger.info("loading model duration: {} for device: {}".format(
    format(time.time() - start_time, '.2f'), device))

app = Flask(__name__)


@app.route('/image', methods=['GET'])
def image():
    try:
        img_url = request.args.get('img_url')
        embedding = process_one(img_url)

        return jsonify(embedding), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/images', methods=['POST'])
def images():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid payload'}), 400

        if 'images' in data:
            image_embeddings = process_images(data['images'])
            return jsonify(image_embeddings), 200
        else:
            return jsonify({'message': 'no data.images'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def process_one(image_url):
    start_time = time.time()
    image = Image.open(requests.get(image_url, stream=True).raw)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    inputs = processor(images=[image], return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embeddings = outputs.squeeze().cpu().tolist()

    logger.info({
        "duration": format(time.time() - start_time, '.2f'),
        "embeddings_length": len(embeddings)
    })

    return {
        "duration": format(time.time() - start_time, '.2f'),
        "embeddings": embeddings
    }


def process_images(image_url_list):
    start_time = time.time()
    images = []
    for i in image_url_list:
        image = Image.open(requests.get(i, stream=True).raw)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        images.append(image)

    inputs = processor(images=images, return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embeddings = outputs.squeeze().cpu().tolist()

    logger.info({
        "duration": format(time.time() - start_time, '.2f'),
        "embeddings_length": len(embeddings)
    })

    return {
        "duration": format(time.time() - start_time, '.2f'),
        "embeddings": embeddings
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
