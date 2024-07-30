from functools import wraps
from flask import current_app, jsonify, request
import logging
import hashlib
import hmac
import time
from flask import request, abort




def validate_signature(payload, signature):
    """
    Validate the incoming payload's signature against our expected signature
    """
    # Use the App Secret to hash the payload
    expected_signature = hmac.new(
        bytes(current_app.config["APP_SECRET"], "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, signature)


def whatsapp_signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Hub-Signature-256", "")[
            7:
        ]  # Removing 'sha256='
        if not validate_signature(request.data.decode("utf-8"), signature):
            logging.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
        return f(*args, **kwargs)

    return decorated_function


def validate_slack_signature(payload, slack_signature, timestamp):
    """
    Validate the incoming payload's signature against the expected signature.
    """
    signing_secret = bytes(current_app.config["SLACK_SIGNING_SECRET"], "latin-1")
    sig_basestring = f"v0:{timestamp}:{payload}"
    expected_signature = 'v0=' + hmac.new(
        signing_secret,
        msg=sig_basestring.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, slack_signature)


def slack_signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct Slack signature.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        slack_signature = request.headers.get("X-Slack-Signature", "")
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")

        # Verifying the request timestamp to protect against replay attacks
        if abs(time.time() - int(timestamp)) > 60 * 5:
            logging.info("Request timestamp is too far from local time!")
            return jsonify({"status": "error", "message": "Invalid timestamp"}), 403

        if not validate_slack_signature(request.get_data(as_text=True), slack_signature, timestamp):
            logging.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403

        return f(*args, **kwargs)

    return decorated_function


def twilio_signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct Slack signature.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        twilio_signature = request.headers.get('X-Twilio-Signature', '')

        # The URL that Twilio is requesting, with the full query string included
        request_url = request.url

        # The POST variables attached to the request, as a dictionary
        request_form = request.form.to_dict()

        # Validate the request using Twilio's SDK
        if not validator.validate(request_url, request_form, twilio_signature):
            print(request_url)
            print(request_form)
            print(twilio_signature)
            print(validator.validate(request_url, request_form, twilio_signature))
            return abort(403)  # If the validation fails, return a 403 Forbidden

        return 'OK', 200
        return f(*args, **kwargs)

    return decorated_function
