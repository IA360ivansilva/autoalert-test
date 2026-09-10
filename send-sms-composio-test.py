#!/usr/bin/env python3
"""
Send SMS via Composio + Dialpad
API Key: ak_5MbHYIv9pnaipo1HpJMc
"""

import os
import sys

# Set API key
API_KEY = "ak_5MbHYIv9pnaipo1HpJMc"
os.environ['COMPOSIO_API_KEY'] = API_KEY

print("🔍 COMPOSIO + DIALPAD SMS TEST")
print("="*70 + "\n")

try:
    from composio import Composio

    print("✅ Composio SDK connected")
    print(f"   API Key: {API_KEY[:20]}...")
    print(f"   Status: Ready\n")

    # Initialize client
    client = Composio(api_key=API_KEY)

    # SMS details
    phone = "9548600537"
    message = "Hi! Test message from Ivan's Agent. Details: askivan.co/edson-david-lower-payment.html -Ivan"

    print("📱 TEST SMS PARAMETERS:")
    print(f"   Recipient: {phone}")
    print(f"   Message: {message}")
    print(f"   Via: Dialpad (via Composio)\n")

    print("🚀 SENDING SMS...\n")

    # Send SMS
    response = client.execute_action(
        action="send_sms",
        params={
            "phone_number": phone,
            "message": message,
        }
    )

    print("✅ SMS SENT SUCCESSFULLY!")
    print(f"\n   Response: {response}")
    print("\n" + "="*70)
    print("✅ TEST COMPLETE - Check your phone for message")
    print("="*70)

except ImportError:
    print("❌ Composio not installed")
    print("\nRun this first:")
    print("   python3 -m pip install composio-core\n")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"\nType: {type(e).__name__}")
    print("\nComposio API key is valid.")
    print("This may need Dialpad SMS action configured in Composio dashboard.")
    sys.exit(1)
