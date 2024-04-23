# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Forked for use in the  WeVoteServer project, September 2020
# see https://firebase.google.com/docs/cloud-messaging/send-message?authuser=0

from __future__ import print_function

import datetime

import firebase_admin
from firebase_admin import messaging
import os
from config.base import get_environment_variable

# Create a real environment variable, from our cached configuration element
try:
    creds_path_from_json = get_environment_variable("GOOGLE_APPLICATION_CREDENTIALS")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path_from_json
    # initialize the firebase admin API, that we use to send Firebase Cloud Messaging (FCM) messages
    default_app = firebase_admin.initialize_app()
    # print('firebase initialized')
except Exception as e:
    pass


def test_msg_to_my_phone():
    # test function
    registration_token = 'eGU5OlHjNg75HGu:APA91bHv0fyc7dr_8Y1h2BL8Z7WSToQI24Uz4sbPYIewDtI7dDX3nRE_4P1RENJNs' \
                         'VVboU142Z-pndTqhnMcCEqCGqkvp36n59Ly7EAPH_1kLJCea_u-6pnkDC8-vjt_oOvZow5r___t'
    send_single_message('IOS', registration_token, "Hello mom", "It is smokey today, like the day before", 2020)
    registration_token = 'c2k5Ew4EQaiyZGuXDpw35t:APA91bHr69JiOxA90hLc7U4pYmPRfYqOWjzijQIPrgiFZSnr4ZwbCv9UawQ_K1UnjOlSEZXij_eMYuK2vZ4FaYljKRRIPG3vctoVlfL4nIEOYgrcdBppAd3a6gdTTaFd7cnwW2jG1Ipi'
    send_single_message('ANDROID', registration_token, "Hello mom", "It is smokey today, again", 2020)


def send_single_message(type, token, title, body, badge_number):
    """
    Send a message to a single device by firebase_fcm_token (from voter_voterdevicelink)
    :param type: 'IOS', 'ANDROID', or 'WEBAPP'
    :param token: The firebase_fcm_token stored in the table from the phone when received from service
    :param title: Title of the message
    :param body: Body of the message
    :param badge_number: The red numeric badge that appears on the icon in iOS
    :return: the response code
    """

    if type == 'IOS':
        message = messaging.Message(
            apns=messaging.APNSConfig(
                headers={'apns-priority': '10'},
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body,
                        ),
                        badge=badge_number,
                    ),
                ),
            ),
            token=token,
        )
    else:
        message = messaging.Message(
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='normal',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    # icon='stock_ticker_update',
                    # color='#f45342'
                ),
            ),
            token=token,
        )

    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    return response


def send_to_token(registration_token):
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_token]


def send_to_topic():
    # [START send_to_topic]
    # The topic name can be optionally prefixed with "/topics/".
    topic = 'highScores'

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        topic=topic,
    )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_topic]


def send_to_condition():
    # [START send_to_condition]
    # Define a condition which will send to devices which are subscribed
    # to either the Google stock or the tech industry topics.
    condition = "'stock-GOOG' in topics || 'industry-tech' in topics"

    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        condition=condition,
    )

    # Send a message to devices subscribed to the combination of topics
    # specified by the provided condition.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_condition]


def send_dry_run():
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token='token',
    )

    # [START send_dry_run]
    # Send a message in the dry run mode.
    response = messaging.send(message, dry_run=True)
    # Response is a message ID string.
    print('Dry run successful:', response)
    # [END send_dry_run]


def android_message():
    # [START android_message]
    message = messaging.Message(
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                title='$GOOG up 1.43% on the day',
                body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        topic='industry-tech',
    )
    # [END android_message]
    return message


def apns_message():

    # [START apns_message]
    message = messaging.Message(
        apns=messaging.APNSConfig(
            headers={'apns-priority': '10'},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title='$GOOG up 1.43% on the day',
                        body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                    ),
                    badge=42,
                ),
            ),
        ),
        topic='industry-tech',
    )
    # [END apns_message]
    return message

def webpush_message():
    # [START webpush_message]
    message = messaging.Message(
        webpush=messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                title='$GOOG up 1.43% on the day',
                body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
                icon='https://my-server/icon.png',
            ),
        ),
        topic='industry-tech',
    )
    # [END webpush_message]
    return message


def all_platforms_message():
    # [START multi_platforms_message]
    message = messaging.Message(
        notification=messaging.Notification(
            title='$GOOG up 1.43% on the day',
            body='$GOOG gained 11.80 points to close at 835.67, up 1.43% on the day.',
        ),
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(badge=42),
            ),
        ),
        topic='industry-tech',
    )
    # [END multi_platforms_message]
    return message


def subscribe_to_topic():
    topic = 'highScores'
    # [START subscribe]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_n',
    ]

    # Subscribe the devices corresponding to the registration tokens to the
    # topic.
    response = messaging.subscribe_to_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were subscribed successfully')
    # [END subscribe]


def unsubscribe_from_topic():
    topic = 'highScores'
    # [START unsubscribe]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_n',
    ]

    # Unubscribe the devices corresponding to the registration tokens from the
    # topic.
    response = messaging.unsubscribe_from_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, 'tokens were unsubscribed successfully')
    # [END unsubscribe]


def send_all():
    registration_token = 'eP80G8ReGU5OlHjNg75HGu:APA91bHv0fyc7dr_8Y1h2BL8Z7WSToQI24Uz4sbPYIewDtI7dDX3nRE_4P1RENJNsVVboU142Z-pndTqhnMcCEqCGqkvp36n59Ly7EAPH_1kLJCea_u-6pnkDC8-vjt_oOvZow5r___t'
    # [START send_all]
    # Create a list containing up to 500 messages.
    messages = [
        messaging.Message(
            notification=messaging.Notification('Price drop', '5% off all electronics'),
            token=registration_token,
        ),
        # ...
        messaging.Message(
            notification=messaging.Notification('Price drop', '2% off all books'),
            topic='readers-club',
        ),
    ]

    response = messaging.send_all(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print('{0} messages were sent successfully'.format(response.success_count))
    # [END send_all]


def send_multicast():
    # [START send_multicast]
    # Create a list containing up to 500 registration tokens.
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_N',
    ]

    message = messaging.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
    )
    response = messaging.send_multicast(message)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print('{0} messages were sent successfully'.format(response.success_count))
    # [END send_multicast]


def send_multicast_and_handle_errors():
    # [START send_multicast_error]
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_N',
    ]

    message = messaging.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
    )
    response = messaging.send_multicast(message)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(registration_tokens[idx])
        print('List of tokens that caused failures: {0}'.format(failed_tokens))
    # [END send_multicast_error]