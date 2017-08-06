rm swot_perderder.zip
zip swot_perderder.zip cmu_pronouncing_dict/** Impact.ttf README.md config.txt food_image_urls.txt foods.txt requirements.txt scrape_images.py sweet_potatoes.jpg swot_perderder.py temp.png
cd env/lib/python2.7/site-packages
find . -name "*" | while read f; do zip -g ../../../../swot_perderder.zip "$f"; done
cd -
