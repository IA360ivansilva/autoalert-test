#!/usr/bin/env python3
"""
Send SMS via Composio + Dialpad integration
Usage: python3 send-sms-via-composio.py --phone 9548600537 --message "Your message"
Or batch: python3 send-sms-via-composio.py --csv /path/to/csv --limit 5
"""

import os
import csv
import json
import sys
import argparse
from datetime import datetime

# Try to import Composio SDK
try:
    from composio import Composio, Action
except ImportError:
    print("❌ Composio SDK not installed")
    print("Install with: pip install composio-core")
    sys.exit(1)

class ComposioSMSClient:
    def __init__(self):
        """Initialize Composio client"""
        # Get API key from environment or use default
        api_key = os.getenv('COMPOSIO_API_KEY', '')

        if not api_key:
            print("⚠️  COMPOSIO_API_KEY not set")
            print("Set it with: export COMPOSIO_API_KEY=your-key-here")
            print("Or configure Composio in your system")

        self.client = Composio(api_key=api_key) if api_key else Composio()
        self.sent_log = []

    def send_sms(self, phone: str, message: str, metadata: dict = None):
        """Send SMS via Composio/Dialpad"""
        try:
            print(f"\n📱 Sending SMS to {phone}...")
            print(f"   Message: {message[:60]}...")

            # Send via Composio SMS action
            # This uses the configured Dialpad/SMS integration
            response = self.client.execute_action(
                action=Action.SEND_SMS,
                params={
                    "phone_number": phone,
                    "message": message,
                }
            )

            # Log the send
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "phone": phone,
                "message_preview": message[:60],
                "status": "sent",
                "response": str(response),
                "metadata": metadata or {}
            }
            self.sent_log.append(log_entry)

            print(f"   ✅ Sent successfully")
            return True

        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "phone": phone,
                "message_preview": message[:60],
                "status": "failed",
                "error": str(e),
                "metadata": metadata or {}
            }
            self.sent_log.append(log_entry)
            return False

    def send_batch_from_csv(self, csv_path: str, limit: int = 5):
        """Send SMS to multiple leads from CSV"""
        if not os.path.exists(csv_path):
            print(f"❌ CSV not found: {csv_path}")
            return

        print(f"\n📋 Processing CSV: {csv_path}")
        print(f"   Limit: {limit} leads\n")

        sent = 0
        skipped = 0
        failed = 0

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if sent >= limit:
                    break

                # Extract data
                nome = row.get('Nome', '').strip()
                primeiro_nome = row.get('Primeiro Nome', '').strip()
                phone = row.get('Cell', '').strip() or row.get('Telefone Principal', '').strip()
                nao_ligar = row.get('Nao Ligar', '').strip().upper()

                # Skip if opted out
                if nao_ligar == 'SIM':
                    print(f"⊘ {primeiro_nome} - opted out (Nao Ligar)")
                    skipped += 1
                    continue

                # Clean phone number
                if not phone:
                    print(f"⊘ {primeiro_nome} - no phone number")
                    skipped += 1
                    continue

                # Remove formatting
                phone_clean = ''.join(c for c in phone if c.isdigit())

                # Create personalized message
                message = f"Hi {primeiro_nome}, we found an opportunity for your Kia. Check details: askivan.co/lead-{phone_clean}.html -Ivan"

                # Send SMS
                success = self.send_sms(
                    phone=phone_clean,
                    message=message,
                    metadata={
                        "customer_name": nome,
                        "customer_id": row.get('Customer ID', ''),
                        "vehicle": row.get('Carro Atual', '')
                    }
                )

                if success:
                    sent += 1
                else:
                    failed += 1

        # Print summary
        print(f"\n{'='*70}")
        print(f"✅ Sent: {sent}")
        print(f"⊘ Skipped: {skipped}")
        print(f"❌ Failed: {failed}")
        print(f"{'='*70}\n")

        # Save log
        log_file = f"sms-log-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.sent_log, f, indent=2)
        print(f"📝 Log saved: {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Send SMS via Composio/Dialpad')
    parser.add_argument('--phone', help='Single phone number (format: 9548600537)')
    parser.add_argument('--message', help='SMS message to send')
    parser.add_argument('--csv', help='CSV file path for batch sending')
    parser.add_argument('--limit', type=int, default=5, help='Max SMS to send from CSV')
    parser.add_argument('--test', action='store_true', help='Test mode (show what would be sent)')

    args = parser.parse_args()

    # Initialize client
    client = ComposioSMSClient()

    # Single SMS
    if args.phone and args.message:
        if args.test:
            print(f"[TEST MODE]")
            print(f"Would send to: {args.phone}")
            print(f"Message: {args.message}")
        else:
            client.send_sms(args.phone, args.message)

    # Batch from CSV
    elif args.csv:
        client.send_batch_from_csv(args.csv, args.limit)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
