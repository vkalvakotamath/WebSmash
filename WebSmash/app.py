from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import random
import itertools
import json


app = Flask(__name__)


# The default image_folder is the Profiles folder located in the repository 
# directory. This is for the use case for dating websites and you'll have to 
# change it if you want some other website.

IMAGE_FOLDER = 'Profiles'


# Get all images from root folder assuming you've run the scraper script. Not really
# sure if it  works since I haven't tested for any dating sites lol.
def get_all_images(root_folder):
    image_files = []
    for subdir, dirs, files in os.walk(root_folder):
        for file in files:

            # Basically scour .png's and .jpg's. Idk about .jpeg.

            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif')):

                rel_path = os.path.relpath(os.path.join(subdir, file), root_folder)
                image_files.append(rel_path.replace('\\', '/'))

    return image_files

def save_ratings():
    with open('ratings.json', 'w') as f:
        json.dump(ratings, f)
        
        # Something is wrong with the indentations and the ordering of these definitions
        # Maybe optimize it.
def initialize_game():
    global images, all_pairs, ratings
    images = get_all_images(IMAGE_FOLDER)
    all_pairs = list(itertools.combinations(images, 2))
    random.shuffle(all_pairs)
    # Start with the usual 1400 default elo,.
    
    ratings = {img: 1400 for img in images}
    save_ratings()

initialize_game()

K = 32

# Elo algorithm with expected_score, update_elo, etc. Needs
# more AI debugging lol. 

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_a, rating_b, score_a):

    expected_a = expected_score(rating_a, rating_b)
    new_rating_a = rating_a + K * (score_a - expected_a)
    new_rating_b = rating_b + K * ((1 - score_a) - (1 - expected_a))
    return new_rating_a, new_rating_b

def load_ratings():
    if os.path.exists('ratings.json'):



        with open('ratings.json', 'r') as f:
            return json.load(f)
    return {img: 1400 for img in images}



def get_txt_content(image_path):
    txt_path = os.path.splitext(os.path.join(IMAGE_FOLDER, image_path))[0] + '.txt'
    if os.path.exists(txt_path):


        with open(txt_path, 'r') as f:


            return f.read()
        

    return "This is the best-match idk."


ratings = load_ratings()


# Debug CD spare_2.py copypasta!!!!

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/Profiles/<path:filename>')

def serve_image(filename):

    return send_from_directory(IMAGE_FOLDER, filename)


# Claude debugged a few things check lmao.


@app.route('/get_pair')
def get_pair():
    if all_pairs:
        pair = all_pairs.pop()
        return jsonify({'image1': pair[0], 'image2': pair[1], 'pairs_left': len(all_pairs)})
    else:
        return jsonify({'finished': True})
    


@app.route('/update_ratings', methods=['POST'])
def update_ratings():


    data = request.json

    winner = data['winner']
    loser = data['loser']

    
    ratings[winner], ratings[loser] = update_elo(ratings[winner], ratings[loser], 1)
    save_ratings()
    
    return jsonify({'success': True})

@app.route('/get_rankings')


def get_rankings():

    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_ratings)

@app.route('/win')
def win():
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_ratings[0]

    txt_content = get_txt_content(winner[0])
    return render_template('win.html', winner=winner, txt_content=txt_content)

# Add restart to let users restart the whole ranking thing.
@app.route('/restart')
def restart():
    initialize_game()
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)