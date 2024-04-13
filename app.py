from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import torch
from PIL import Image
import requests
import time
import sys
import random
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
processor = CLIPProcessor.from_pretrained(LOCAL_MODEL_DIR)
model.to(device)
logger.info("loading image model duration: {} for device: {}".format(
    format(time.time() - start_time, '.2f'), device))

start_time = time.time()
textModelPath = '/opt/models/all-mpnet-base-v2'
# textModel = SentenceTransformer('all-mpnet-base-v2')
# textModel.save(textModelPath)
textModel = SentenceTransformer(textModelPath)
logger.info("loading text model duration: {} for device: {}".format(
    format(time.time() - start_time, '.2f'), device))

app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"now.now": time.time()}), 200


@app.route('/smoke', methods=['GET'])
def smoke():
    try:
        start_time = time.time()
        image = Image.open('s/p_00{}.jpg'.format(random.randint(1, 5)))
        duration_downalod = format(time.time() - start_time, '.2f')
        embedding = process_one(image)
        embedding['duration_download'] = duration_downalod
        return jsonify(embedding), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/smoke10', methods=['GET'])
def smoke10():
    try:
        start_time = time.time()
        images = []
        for iter in range(0, 10):
            image = Image.open('s/p_00{}.jpg'.format((iter % 5) + 1))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            images.append(image)
        duration_downalod = format(time.time() - start_time, '.2f')

        embedding = process_images(images)
        embedding['duration_download'] = duration_downalod
        return jsonify(embedding), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image-text', methods=['GET'])
def image_text():
    try:
        start_time = time.time()
        img_url = request.args.get('img_url')
        text_input = request.args.get('text').split("|")
        image = Image.open(requests.get(img_url, stream=True).raw)
        duration_downalod = format(time.time() - start_time, '.2f')
        probs = match_image_text(image, text_input)
        probs['img_url'] = img_url
        probs['duration_download'] = duration_downalod

        return jsonify(probs), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image-image', methods=['GET'])
def image_image():
    try:
        start_time = time.time()
        img_url1 = request.args.get('img_url1')
        img_url2 = request.args.get('img_url2')
        image1 = Image.open(requests.get(img_url1, stream=True).raw)
        image2 = Image.open(requests.get(img_url2, stream=True).raw)
        duration_downalod = format(time.time() - start_time, '.2f')

        probs = match_image_image(image1, image2)
        probs['duration_download'] = duration_downalod
        probs['img_url1'] = img_url1
        probs['img_url2'] = img_url2
        return jsonify(probs), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image', methods=['GET'])
def image():
    try:
        start_time = time.time()
        img_url = request.args.get('img_url')
        image = Image.open(requests.get(img_url, stream=True).raw)
        duration_downalod = format(time.time() - start_time, '.2f')
        embedding = process_one(image)
        embedding['duration_download'] = duration_downalod
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
            start_time = time.time()
            images = []
            for i in data['images']:
                image = Image.open(requests.get(i, stream=True).raw)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                images.append(image)
            duration_downalod = format(time.time() - start_time, '.2f')

            embedding = process_images(images)
            embedding['duration_download'] = duration_downalod
            return jsonify(embedding), 200
        else:
            return jsonify({'message': 'no data.images'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def process_one(image):
    start_time = time.time()

    if image.mode != 'RGB':
        image = image.convert('RGB')

    inputs = processor(images=[image], return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embeddings = outputs.squeeze().cpu().tolist()

    logger.info({
        "duration_features": format(time.time() - start_time, '.2f'),
        "embeddings_length": len(embeddings)
    })

    return {
        "duration_features": format(time.time() - start_time, '.2f'),
        "embeddings": embeddings
    }


@app.route('/text-sim', methods=['GET'])
def text_sim():
    try:
        start_time = time.time()
        text_input = request.args.get('text').split("|")
        if len(text_input) < 2:
            return jsonify({
                "message":
                "minimal text array must be 2. input is {}".format(
                    len(text_input))
            }), 200
        text_embeddings = textModel.encode(text_input).tolist()
        duration_embedding = format(time.time() - start_time, '.2f')

        cos_sims = cos_sim(text_embeddings[0], text_embeddings[1:]).tolist()[0]
        sims = {}
        for index in range(len(cos_sims)):
            sims[text_input[index + 1]] = cos_sims[index]

        rs = {
            "duration_embedding": duration_embedding,
            "sim_compare_to": text_input[0],
            "sim_scores": sims
        }
        return jsonify(rs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/text', methods=['GET'])
def text():
    try:
        start_time = time.time()
        text_input = request.args.get('text')
        text_embeddings = textModel.encode([text_input]).tolist()[0]

        rs = {
            "duration_features": format(time.time() - start_time, '.2f'),
            "embeddings": text_embeddings
        }
        return jsonify(rs), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def match_image_text(image, text_input):
    start_time = time.time()
    if image.mode != 'RGB':
        image = image.convert('RGB')

    inputs = processor(text=text_input,
                       images=image,
                       return_tensors="pt",
                       padding=True)
    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1).tolist()[0]
    sims = {}
    for i, t in enumerate(text_input, start=0):
        sims[t] = probs[i]

    logger.info({
        "duration_features": format(time.time() - start_time, '.2f'),
        "probs": sims
    })

    return {
        "duration_features": format(time.time() - start_time, '.2f'),
        "probs": sims
    }


def match_image_image(image1, image2):
    start_time = time.time()
    if image1.mode != 'RGB':
        image1 = image1.convert('RGB')
    if image2.mode != 'RGB':
        image2 = image2.convert('RGB')

    input1 = processor(images=[image1], return_tensors="pt")
    input2 = processor(images=[image2], return_tensors="pt")
    input1 = input1.to(device)
    input2 = input2.to(device)

    # Calculate the embeddings for the images using the CLIP model
    with torch.no_grad():
        embedding_a = model.get_image_features(**input1)
        embedding_b = model.get_image_features(**input2)

    # Calculate the cosine similarity between the embeddings
    similarity_score = torch.nn.functional.cosine_similarity(
        embedding_a, embedding_b)

    # Print the similarity score
    print('Similarity score:', similarity_score.item())

    logger.info({
        "duration_features": format(time.time() - start_time, '.2f'),
        "probs": similarity_score.item()
    })

    return {
        "duration_features": format(time.time() - start_time, '.2f'),
        "probs": similarity_score.item()
    }


def process_images(images):
    start_time = time.time()
    inputs = processor(images=images, return_tensors="pt")
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    embeddings = outputs.squeeze().cpu().tolist()

    logger.info({
        "duration_features": format(time.time() - start_time, '.2f'),
        "embeddings_length": len(embeddings)
    })

    return {
        "duration_features": format(time.time() - start_time, '.2f'),
        "embeddings": embeddings
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
