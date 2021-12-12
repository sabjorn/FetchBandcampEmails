from __future__ import print_function
import pickle
import os.path
import base64
import argparse
import logging
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from bs4 import BeautifulSoup

SEARCH_TERMS = [
    "just released", # new releases
    "bought new music on" # from followed users
]

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def create_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # # The file token.pickle stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def get_messages(query_term):
    request = service.users().messages().list(userId='me', q=f"from:noreply@bandcamp.com \"{query_term}\"", labelIds="UNREAD")
    response = request.execute()
    messages = response.get('messages', [])
    while response.get('nextPageToken'):
        request = service.users().messages().list_next(previous_request=request, previous_response=response)
        response = request.execute()
        messages += response['messages']
    return messages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Finds unread emails from bandcamp and creates a list of URLs and marks emails as read.")
    parser.add_argument(
        "-m",
        "--mark",
        help="mark found emails as read",
        action="store_true")
    parser.add_argument(
        "-o",
        "--outfile",
        help="optional: directory for printing files, prints to screen otherwise",
        type=str,
        default=None)
    args = parser.parse_args()

    service = create_service()

    # NOTE: service above must come first, interacts poorly with logger
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    messages = []
    for term in SEARCH_TERMS:
        messages += get_messages(term)

    if not len(messages):
        logger.info('No messages found.')
        exit()
    
    urls = set()
    for message in messages:
        request = service.users().messages().get(userId='me', id=message['id'], format="raw")
        response = request.execute()
        
        raw = base64.urlsafe_b64decode(response['raw'])
        raw_cleaned = raw.replace(b"=0D\r\n",b"").replace(b"=\r\n", b"").replace(b"3D",b"")

        soup = BeautifulSoup(raw_cleaned, 'html.parser')
        for a in soup.find_all('a'):
            href = a.get('href')
            if "bandcamp.com/album/" in href:
                url = href.split('?')[0]
                urls.add(url)

    try:
        with open(args.outfile, "w") as f:
            for url in urls:
                f.write(url+"\n")
        logger.info(f"writing to {args.outfile}")
    except TypeError as e:
        logger.info("no output file found, printing to stdout")
        for url in urls:
            sys.stdout.write(f"{url}\n")
        pass
    except Exception as e:
        logger.exception("error in generation of data")

    if args.mark:
        logger.info("marking messages as read")
        for message in messages:
            request = service.users().messages().modify(userId="me", id=message['id'], body={"removeLabelIds": ["UNREAD"]})
            response = request.execute()
