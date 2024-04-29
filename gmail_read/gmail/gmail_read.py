# importing libraries required
import json
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import base64
from bs4 import BeautifulSoup

from gmail.models import Emails
from gmail_read.settings import BASE_DIR

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authorize_email_account():
    # user access token
    user_token = None
    gmail_service = ''

    try:
        # read if the token exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                user_token = pickle.load(token)

        # ask user to login if token not exists and save the token
        if not user_token or not user_token.valid:
            if user_token and user_token.expired and user_token.refresh_token:
                user_token.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(BASE_DIR) + '/config/credentials.json', SCOPES)
                user_token = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(user_token, token)

        # connecting to gmail API
        gmail_service = build('gmail', 'v1', credentials=user_token)
    except Exception as e:
        print(str(e))

    return gmail_service


def get_emails_list(gmail_service, user_id, label_ids=[]):
    # fetch and store emails list
    emails = gmail_service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
    # emails = gmail_service.users().messages().list(userId='me', maxResults=100).execute()

    messages = []
    if 'messages' in emails:
        messages.extend(emails['messages'])

    while 'nextPageToken' in emails:
        page_token = emails['nextPageToken']
        response = gmail_service.users().messages().list(userId=user_id,
                                                         labelIds=label_ids,
                                                         pageToken=page_token).execute()
        messages.extend(response['messages'])

    # iterate through all the messages
    try:
        for msg in messages:
            text = gmail_service.users().messages().get(userId=user_id, id=msg['id']).execute()

            try:
                payload = text['payload']
                headers = payload['headers']
                # print('headers ------ ', headers)
                for i in headers:
                    if i['name'] == 'Subject':
                        subject = i['value']
                    if i['name'] == 'From':
                        sender = i['value']
                    if i['name'] == 'Date':
                        msg_date = i['value']
                    if i['name'] == 'Message-ID':
                        msg_id = i['value']
                    if i['name'] == 'To':
                        mail_to = i['value']

                    msg_date = " ".join(msg_date.split()[:5])
                    converted_date = time.strptime(msg_date, "%a, %d %b %Y %H:%M:%S")
                    msg_date = time.strftime("%Y-%m-%d %H:%M:%S", converted_date)

                    parts = payload.get('parts')[0]
                    data = parts['body']['data']
                    data = data.replace('-', '+').replace("_", "/")
                    decoded_data = base64.b64decode(data)

                    soup = BeautifulSoup(decoded_data, 'lxml')
                    body = soup.body()
                    Emails.objects.get_or_create(email_from=sender, send_to_mail=mail_to, subject=subject,
                                                 message_id=msg_id, message=body, message_date=msg_date)
                    # print(subject, '---------------', sender, '---------------', body)
            except Exception as e:
                print(str(e))
                pass

            return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(str(e))


def fetch_all_labels(gmail_service, user_id):
    results = gmail_service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])

    return labels


def apply_email_rules():
    rules = json.load(open('rules.json'))
    for rule in rules["1"]["criteria"]:
        print(rule['name'], rule['value'])
        field_name = "email_" + rule['name']
        filter_kwargs = {field_name: rule['value'][1]}
        queryset = Emails.objects.filter(**filter_kwargs)


def main():
    user_id = 'me'
    gmail_service = authorize_email_account()
    labels_list = fetch_all_labels(gmail_service, user_id)
    fetch_emails = get_emails_list(gmail_service, user_id, labels_list)
    apply_email_rules()


if __name__ == '__main__':
    main()
