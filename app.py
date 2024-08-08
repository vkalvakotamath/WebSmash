from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import random
import itertools
from itertools import combinations
import json
import arxiv

app = Flask(__name__)

# Global variables
IMAGE_FOLDER = 'Profiles'
images = []
papers = []
all_pairs = []
all_combinations = []
ratings = {}
current_mode = None
current_category = None
K = 32

# Image handling functions
def get_all_images(root_folder):
    image_files = []
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif')):
                rel_path = os.path.relpath(os.path.join(subdir, file), root_folder)
                image_files.append(rel_path.replace('\\', '/'))
    return image_files

def get_txt_content(image_path):
    txt_path = os.path.splitext(os.path.join(IMAGE_FOLDER, image_path))[0] + '.txt'
    if os.path.exists(txt_path):
        with open(txt_path, 'r') as f:
            return f.read()
    return "No additional information available."

def fetch_arxiv_papers(category, max_results=4):
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    return list(client.results(search))

# Game initialization
def initialize_local_game():
    global images, all_pairs, ratings, current_mode
    current_mode = 'local'
    images = get_all_images(IMAGE_FOLDER)
    all_pairs = list(itertools.combinations(images, 2))
    random.shuffle(all_pairs)
    ratings = {img: 1400 for img in images}
    save_ratings()

def initialize_arxiv_game(category):
    global papers, all_combinations, ratings, current_mode, current_category
    current_mode = 'arxiv'
    current_category = category
    papers = fetch_arxiv_papers(category)
    all_combinations = list(combinations(papers, 2))
    random.shuffle(all_combinations)
    ratings = {paper.entry_id: 1400 for paper in papers}

# Elo rating functions
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_a, rating_b, score_a):
    expected_a = expected_score(rating_a, rating_b)
    new_rating_a = rating_a + K * (score_a - expected_a)
    new_rating_b = rating_b + K * ((1 - score_a) - (1 - expected_a))
    return new_rating_a, new_rating_b

# About page thingy

@app.route('/about')
def about():
    return render_template('about.html')


# Local help page thingy


@app.route('/local_help')
def local_help():
    return render_template('local_help.html')


# File handling functions
def save_ratings():
    with open('ratings.json', 'w') as f:
        json.dump(ratings, f)

def load_ratings():
    if os.path.exists('ratings.json'):
        with open('ratings.json', 'r') as f:
            return json.load(f)
    return {img: 1400 for img in images}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_mode', methods=['POST'])
def select_mode():
    mode = request.form['mode']
    if mode == 'local':
        initialize_local_game()
        return redirect(url_for('rate_local'))
    elif mode == 'arxiv':
        categories = ['gr-qc', 'hep-th', 'astro-ph', 'cond-mat', 'quant-ph']
        return render_template('select_category.html', categories=categories)

@app.route('/set_category', methods=['POST'])
def set_category():
    category = request.form['category']
    initialize_arxiv_game(category)
    return redirect(url_for('rate_arxiv'))

@app.route('/rate_local')
def rate_local():
    return render_template('rate_local.html')

@app.route('/rate_arxiv')
def rate_arxiv():
    return render_template('rate_arxiv.html')

@app.route('/get_pair')
def get_pair():
    if current_mode == 'local':
        if all_pairs:
            pair = all_pairs.pop()
            return jsonify({'image1': pair[0], 'image2': pair[1], 'pairs_left': len(all_pairs)})
        else:
            return jsonify({'finished': True})
    else:
        return jsonify({'error': 'Invalid mode'})

@app.route('/get_combination')
def get_combination():
    if current_mode == 'arxiv':
        if all_combinations:
            combination = all_combinations.pop(0)  # Use pop(0) instead of random.choice
            return jsonify({
                'paper1': {
                    'id': combination[0].entry_id,
                    'title': combination[0].title,
                    'authors': ', '.join(author.name for author in combination[0].authors),
                    'abstract': combination[0].summary,
                    'pdf_url': combination[0].pdf_url
                },
                'paper2': {
                    'id': combination[1].entry_id,
                    'title': combination[1].title,
                    'authors': ', '.join(author.name for author in combination[1].authors),
                    'abstract': combination[1].summary,
                    'pdf_url': combination[1].pdf_url
                },
                'combinations_left': len(all_combinations)
            })
        else:
            return jsonify({'finished': True})
    else:
        return jsonify({'error': 'Invalid mode'})

@app.route('/update_ratings', methods=['POST'])
def update_ratings():
    data = request.json
    if current_mode == 'local':
        winner = data['winner']
        loser = data['loser']
        ratings[winner], ratings[loser] = update_elo(ratings[winner], ratings[loser], 1)
        save_ratings()
    elif current_mode == 'arxiv':
        winner_id = data['winner']
        loser_ids = data['losers']
        for loser_id in loser_ids:
            ratings[winner_id], ratings[loser_id] = update_elo(ratings[winner_id], ratings[loser_id], 1)
    return jsonify({'success': True})

@app.route('/get_rankings')
def get_rankings():
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ratings)

@app.route('/win')
def win():
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_ratings[0]
    if current_mode == 'local':
        txt_content = get_txt_content(winner[0])
        return render_template('win_local.html', winner=winner, txt_content=txt_content)
    elif current_mode == 'arxiv':
        winner_id = winner[0]
        winner_paper = next(paper for paper in papers if paper.entry_id == winner_id)
        return render_template('win_arxiv.html', paper=winner_paper, score=winner[1])

@app.route('/restart')
def restart():
    return redirect(url_for('index'))

@app.route('/Profiles/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)