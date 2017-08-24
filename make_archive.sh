rm swot_perderder.zip
cd env/lib/python3.6/site-packages
zip -r9 ../../../../swot_perderder.zip *
cd ../../../..
zip -g swot_perderder.zip -r cmu_pronouncing_dict Impact.ttf config.txt foods.txt swot_perderder.py
