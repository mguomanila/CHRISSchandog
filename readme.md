# activate crontab
1. execute the command:
```
crontab -e
```
2. then copy paste the content of `crontab.txt`.
3. exit and save ... that's all.

# description
1. `amazon4` is the first crawler to copy the url links
2. `amazon3` is the second crawler to extract all the detailed information

# create virtual env and install requirements
1. Create the virtual env directory: `python -m virtualenv virtualenv_python3`
2. Activate the virtual env: `source virtualenv_python3/bin/activate`
3. Install requirements for this project: 
```
pip install -r requirements.txt
```

# how to use the crawler
1. Remember to setup the database credentials in `settings.py`
2. run `scrapy crawler amazon4` to run the url crawlers
3. run `scrapy crawler amazon3` to run the detailed info crawlers
