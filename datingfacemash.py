# Pseudo copypasta from the PaperRetriever
# project because wtf. Also this is probably 
# illegal but idk. 

import os
import requests
from bs4 import BeautifulSoup
import json

# Try wget at the chance of redundancy for smoother requests?
# Not really sure how functionally different from requests.

import wget


BASE_URL = "SOME DATING WEBSITE URL."

# Add the search query URL so that the entered search query is 
# searched in the BASE_URL

SEARCH_URL = f"{BASE_URL}/search?query="

base_dir = "WebSmash"

profiles_dir = os.path.join(base_dir, "Profiles")
os.makedirs(profiles_dir, exist_ok=True)

def get_profile(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    name = soup.select_one('.profile-name').text.strip()

    age = soup.select_one('.profile-age').text.strip()
    
    bio = soup.select_one('.profile-bio').text.strip()
    picture_url = soup.select_one('.profile-picture img')['src']
    
    return {
        'name': name,
        'age': age,
        'bio': bio,
        'picture_url': picture_url
    }




def search_profiles(query):
    url = SEARCH_URL + query
    response = requests.get(url)

    # BeautifulSoup html.parser
    soup = BeautifulSoup(response.text, 'html.parser')

    profile_links = soup.select('.profile-card a')
    return [BASE_URL + link['href'] for link in profile_links]
def save_profile(profile_data):
    profile_name = profile_data['name'].replace(" ", "_").lower()
    profile_dir = os.path.join("WebSmash", "Profiles", profile_name)
    os.makedirs(profile_dir, exist_ok=True)

    
    # Save metadata from profiles and store into profile_name.txt files.

    # MAKE SURE that the image names and the corresponding profile/metadata
    # files have the same name, or the elo ranking algorithm won't show the 
    # best fit with info. Or if you're only into faces that works too 
    # I guess.

    
    with open(os.path.join(profile_dir, f"{profile_name}.txt"), "w") as f:

        json.dump(profile_data, f, indent=2)

    try:
        wget.download(profile_data['picture_url'], out=os.path.join(profile_dir, f"{profile_name}.jpg"))

        # Print saved profile_name stuff
        
        print(f"\nSaved {profile_name}")
    except Exception as e:
        print(f"\nSomething went wrong, please try again.")

def main():
    query = input("Enter your search queries: ")

    # prfile_urls =- search_profiles query
    
    profile_urls = search_profiles(query)
    
    for url in profile_urls:
        profile_data = get_profile(url)
        save_profile(profile_data)
        print(f"Saved profile for {profile_data['name']}")

if __name__ == "__main__":
    main()