import json
import os
import argparse
import urllib.request
import urllib.error
import http.cookiejar
from datetime import datetime

def get_apply_type_name(value):
    mapping = {
        2: "LOTTERY",
        3: "SALE"
    }
    return mapping.get(value, f"UNKNOWN({value})")

def get_sale_status_name(value):
    mapping = {
        1: "SALE",
        2: "SOLD_OUT"
    }
    return mapping.get(value, f"UNKNOWN({value})")

def get_open_status_name(value):
    mapping = {
        1: "OPEN",
        2: "REGULAR_HOLIDAY"
    }
    return mapping.get(value, f"UNKNOWN({value})")

def fetch_data_from_api(year, month):
    # Setup cookie jar and opener
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    # Common headers for main page visit (Navigation)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://museum-tickets.nintendo.com/en/calendar",
        "Origin": "https://museum-tickets.nintendo.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Upgrade-Insecure-Requests": "1",
    }

    # Step 1: Visit the main calendar page to initialize cookies/session
    main_page_url = "https://museum-tickets.nintendo.com/en/calendar"
    print(f"visiting main page: {main_page_url}")
    try:
        req = urllib.request.Request(main_page_url, headers=headers)
        with opener.open(req) as response:
            # Just read response to ensure cookies are set
            response.read()
    except Exception as e:
         print(f"Error visiting main page: {e}")
         # Continue anyway, maybe it works without pre-visit
    
    # Step 2: Call the API
    api_url = f"https://museum-tickets.nintendo.com/en/api/calendar?target_year={year}&target_month={month}"
    print(f"Fetching data from: {api_url}")
    
    # Update headers for JSON API request (XHR/Fetch)
    api_headers = headers.copy()
    api_headers["Accept"] = "application/json, text/plain, */*"
    api_headers["Sec-Fetch-Dest"] = "empty"
    api_headers["Sec-Fetch-Mode"] = "cors"
    api_headers["X-Requested-With"] = "XMLHttpRequest"
    # Remove navigation-specific headers if necessary, but usually safe to keep or overwrite
    del api_headers["Upgrade-Insecure-Requests"]

    try:
        req = urllib.request.Request(api_url, headers=api_headers)
        with opener.open(req) as response:
            final_url = response.geturl()
            if final_url != api_url:
                 print(f"Warning: Request was redirected to: {final_url}")

            raw_data = response.read().decode()
            try:
                return json.loads(raw_data)
            except json.JSONDecodeError as e:
                print(f"Error Decoding JSON: {e}")
                print("Raw Response Body START:")
                print(raw_data)
                print("Raw Response Body END")
                return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print("Response Headers:")
        print(e.headers)
        print("Response Body:")
        print(e.read().decode())
        return None
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
        if hasattr(e, 'read'):
             print(f"Response body: {e.read().decode()}")
        return None

def load_data_from_file(file_path):
    print(f"Loading data from file: {file_path}")
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'.")
        return None

def main():
    parser = argparse.ArgumentParser(description='Check Nintendo Museum ticket availability.')
    parser.add_argument('--year', type=int, help='Target year (e.g., 2026)')
    parser.add_argument('--month', type=str, help='Target month (1-12) or range (e.g. "2-4")')
    parser.add_argument('--file', type=str, help='Path to local JSON file (for testing)')
    parser.add_argument('--dry-run-email', action='store_true', help='Print email body instead of sending')
    parser.add_argument('--always-send', action='store_true', help='Send email even if no tickets are found')
    
    args = parser.parse_args()

    if args.file:
        # File mode (single file)
        data = load_data_from_file(args.file)
        if data:
            output_text, has_tickets = process_calendar_data(data, "File: " + args.file)
            print(output_text)
            
            subject = "Nintendo Museum Tickets ALERT" if has_tickets else "Nintendo Museum Tickets Not Available"
            
            should_send = has_tickets or args.always_send

            if should_send:
                if args.dry_run_email:
                     print(f"\n[Dry Run] Would send email to peterrhysthomas@yahoo.co.uk from peter.thomastechnology@gmail.com using smtp.gmail.com:587")
                     print(f"Subject: {subject}")
                     print(f"Body:\n{output_text}")
                else:
                     send_email(output_text, subject)
            else:
                print("\nEmail not sent (Use --always-send to force sending when no tickets are found).")
        return

    # API Mode
    now = datetime.now()
    year = args.year if args.year else now.year
    
    target_months = []
    if args.month:
        if '-' in args.month:
            start, end = map(int, args.month.split('-'))
            target_months = list(range(start, end + 1))
        elif ',' in args.month:
             target_months = [int(m) for m in args.month.split(',')]
        else:
            target_months = [int(args.month)]
    else:
        # Default to next month if not specified
        next_month = (now.month % 12) + 1
        target_months = [next_month]
        if next_month == 1: # Wrapped around to Jan
             year += 1

    all_calendar_data = {}
    
    for month in target_months:
        # Handle year rollover if needed (though user usually specifies year)
        # For simplicity, assuming the specified year applies to all months provided
        # unless it's the default logic above.
        
        # print(f"\n--- Checking {year}-{month:02d} ---") # Removed per collation rq
        data = fetch_data_from_api(year, month)
        if data and 'data' in data and 'calendar' in data['data']:
             all_calendar_data.update(data['data']['calendar'])

    if all_calendar_data:
        # Create a synthetic data structure to reuse process_calendar_data logic
        synthetic_data = {'data': {'calendar': all_calendar_data}}
        output_text, has_tickets = process_calendar_data(synthetic_data, f"{year} Months: {args.month}")
        print(output_text)
        
        subject = "Nintendo Museum Tickets ALERT" if has_tickets else "Nintendo Museum Tickets Not Available"
        
        should_send = has_tickets or args.always_send

        if should_send:
            if args.dry_run_email:
                 print(f"\n[Dry Run] Would send email to peterrhysthomas@yahoo.co.uk from peter.thomastechnology@gmail.com using smtp.gmail.com:587")
                 print(f"Subject: {subject}")
                 print(f"Body:\n{output_text}")
            else:
                 send_email(output_text, subject)
        else:
            print("\nEmail not sent (Use --always-send to force sending when no tickets are found).")
    else:
        print("No data found for the specified range.")

def process_calendar_data(data, source_name):
    if not data:
        return "", False

    # Check if expected structure exists
    if 'data' not in data or 'calendar' not in data['data']:
        return "Error: JSON structure does not match expected format (data.calendar).", False

    calendar_data = data['data']['calendar']
    
    # Sort dates to ensure chronological order
    dates = sorted(calendar_data.keys())
    
    full_table = []
    header = f"{'Date':<12} | {'Apply Type':<12} | {'Sale Status':<12} | {'Open Status':<15}"
    full_table.append(header)
    full_table.append("-" * len(header))
    
    sale_open_days = []

    for date_str in dates:
        day_data = calendar_data[date_str]
        apply_type = day_data.get('apply_type')
        sale_status = day_data.get('sale_status')
        open_status = day_data.get('open_status')
        
        full_table.append(f"{date_str:<12} | {get_apply_type_name(apply_type):<12} | {get_sale_status_name(sale_status):<12} | {get_open_status_name(open_status):<15}")

        # Check for SALE (1) and OPEN (1)
        if sale_status == 1 and open_status == 1:
            sale_open_days.append(date_str)

    # Reordering Output: Found Days First
    output = []
    
    if sale_open_days:
        output.append("="*30)
        output.append(f"FOUND {len(sale_open_days)} day(s) with SALE and OPEN status in [{source_name}]:")
        for day in sale_open_days:
            output.append(f"- {day}")
        output.append("="*30)
        output.append("") # Spacer
    else:
        output.append("="*30)
        output.append(f"NO days found with SALE and OPEN status in [{source_name}].")
        output.append("="*30)
        output.append("")

    # Then append the full table
    output.extend(full_table)
    
    return "\n".join(output), bool(sale_open_days)

import smtplib
from email.mime.text import MIMEText

def send_email(body, subject):
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "peter.thomastechnology@gmail.com"
    smtp_password = os.environ.get("SMTP_PASSWORD")
    to_email = "peterrhysthomas@yahoo.co.uk"

    if not smtp_password:
        print("Warning: SMTP_PASSWORD not found in environment variables. Email not sent.")
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    main()
