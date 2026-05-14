"""
frontend/auth/twilio_auth.py
─────────────────────────────
All Twilio Verify SMS OTP logic.
Reads credentials from environment variables (set in .env).
"""

import os
import streamlit as st


def send_phone_otp(phone: str) -> bool:
    """
    Send a 6-digit OTP to the given phone number via Twilio Verify.
    Phone must include country code e.g. +919876543210
    Returns True if OTP was dispatched (status == 'pending').
    """
    try:
        from twilio.rest import Client

        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        verification = client.verify.v2.services(
            os.environ["TWILIO_VERIFY_SID"]
        ).verifications.create(to=phone, channel="sms")

        return verification.status == "pending"

    except ImportError:
        st.error("Twilio not installed. Run: pip install twilio")
        return False

    except KeyError as missing:
        st.error(
            f"Missing environment variable: {missing}. "
            "Make sure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and "
            "TWILIO_VERIFY_SID are set in your .env file."
        )
        return False

    except Exception as e:
        st.error(f"Could not send SMS OTP: {e}")
        return False


def verify_phone_otp(phone: str, code: str) -> bool:
    """
    Verify the 6-digit OTP code for the given phone number.
    Returns True if the code is correct (status == 'approved').
    """
    try:
        from twilio.rest import Client

        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        result = client.verify.v2.services(
            os.environ["TWILIO_VERIFY_SID"]
        ).verification_checks.create(to=phone, code=code)

        return result.status == "approved"

    except Exception as e:
        st.error(f"OTP verification failed: {e}")
        return False
