import logging
import json

from flask import Blueprint, request, jsonify, current_app

from datetime import datetime

from .decorators.security import whatsapp_signature_required, twilio_signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message
)
from flask import request, Response


webhook_blueprint = Blueprint("webhook", __name__)


def handle_message(req_time):
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    # logging.info(f"request body: {body}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body, req_time)
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API or Slack API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    logging.info("inside verify")
    print(request)
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            print(f"Mode: {mode}, Token: {token}, Verify token: {current_app.config['VERIFY_TOKEN']}, Challenge: {challenge}")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/")
def hello():
    return 'Service is up!'




@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()


# @webhook_blueprint.route("/hitesh", methods=["POST"])
# def hitesh_func():
#     return "Yes, it's working :)"


@webhook_blueprint.route("/webhook", methods=["POST"])
@whatsapp_signature_required
def webhook_post():
    req_time = datetime.now().time().isoformat(timespec='milliseconds')
    return handle_message(req_time)


