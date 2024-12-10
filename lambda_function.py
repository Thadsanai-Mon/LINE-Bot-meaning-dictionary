import os
import json
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Environment variables for LINE Channel Access Token and Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'LINE_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'LINE_CHANNEL_SECRET'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def lambda_handler(event, context):
    headers = event["headers"]
    body = event["body"]

    # Verify the LINE signature
    signature = headers["x-line-signature"]
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid signature"})}

    return {"statusCode": 200, "body": json.dumps({"message": "Success"})}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text  # The word input from the user

    # Query Dictionary API
    response = requests.get(f"{DICTIONARY_API_URL}{user_message}")
    if response.status_code != 200:
        reply_message = f"Sorry, I couldn't find the definition for '{user_message}'."
    else:
        dictionary_data = response.json()
        reply_message = format_dictionary_response(dictionary_data)

    # Reply to the user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )


def format_dictionary_response(data):
    """Format the dictionary API response for the chatbot."""
    try:
        word = data[0]["word"]
        meanings = data[0]["meanings"]

        response_text = ""
        
        for meaning in meanings[:2]:  # Limit to 2 parts of speech
            part_of_speech = meaning["partOfSpeech"]
            definitions = meaning["definitions"]
            for definition in definitions[:1]:  # Limit to 1 definition per part of speech
                response_text += f"■ {part_of_speech.capitalize()}: {definition['definition']}\n"

        return response_text
    except Exception as e:
        return "Error formatting the dictionary response."
