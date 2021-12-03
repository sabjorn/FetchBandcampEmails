# FetchBandcampEmails
## About
Helper script which uses the Gmail API to find new release emails from Bandcamp.

## Setup
### Gmail API Credentials
The easiest way to setup credentials is to go to the Pythong quickstart page:

https://developers.google.com/gmail/api/quickstart/python

Scroll down and click: `Enable the Gmail API`

After accepting everything, download the `credentials.json` file and place it in the top level of this project (i.e. `./FetchBandcampEmails/credentials.json`)

Alternatively, follow this:

https://medium.com/@stevelukis/using-python-and-gmail-api-to-retrieve-list-of-senders-to-our-email-be3249f1a6db

**Note**: **DO NOT SHARE THIS FILE** BUT maybe put it in your password manager ;)

### Python
run:
```
python -m venv .venv 
source .venv/bin/activate
pip install -r requirements
```

## Running
## Basic Command
```
python FetchBandcampEmails.py
```

**Note**: The first time you run the command you will be required to login to your gmail account. A file will be created--`token.pickle`--which is used by the script to prevent the need of loging in again. **DO NOT SHARE THIS FILE**

## Command Line Options
* `-o`, `--outfile` - *optional* output file for URL list
* `-m`, `--mark` - *optional* mark found emails as read (remove `UNREAD` label)
