Write a python script to access data from the Nintendo museum website calendar of tickets and determine whether any tickets are available for purchase.

The website page is https://museum-tickets.nintendo.com/en/calendar and this uses a call to a calendar api to get the data for a given month and year.

There is example data in the file calendar_mar.json, this matches the data which would be returned by the api if called as follows 'https://museum-tickets.nintendo.com/en/api/calendar?target_year=2026&target_month=2'

Implement all required functionality to ensure that a request is made.  This would include setting up cookies and headers to mimic a real browser request.  If the request fails, print out all the return response including the http codes.  Implement bot protection bypass if the api response returns a non-json response.

Tickets are available for purchase if there are any days with sale status of sale and open status of open.

The data below details the json decode rules for the calendar data.

apply_type - 
        LOTTERY: 2,
        SALE: 3
sale_status - 
        SALE: 1,
        SOLD_OUT: 2
open_status - 
        OPEN: 1,
        REGULAR_HOLIDAY: 2


Allow the script to be called with a range of months to check tickets for, e.g 2-4 would check February and March and April. If multiple months are provided, all data should be collated into a single output.

Email Output:
Once the output is produced, this should be formed into an email and sent to the email address [peterrhysthomas@yahoo.co.uk] from the email address [peter.thomastechnology@gmail.com], add in the relevant SMTP server details to allow this to work.

The email should have the title 'Nintendo Museum Tickets Not Available' if no tickets are available, or 'Nintendo Museum Tickets ALERT' if tickets are available. Within the body of the email, first show any days with availability and then after show the entire table.  At the top of the email body, put the link to the calendar webpage 'https://museum-tickets.nintendo.com/en/calendar'

The script should take a parameter to indicate whether to send the email or not.  If the parameter is not provided, the script should not send the email in the case of there being no tickets available.  If there are tickets available, the script should send the email.

Bluesky Output:
Once the output is produced, this should be formed into a Bluesky post and sent to the Bluesky account 'prt12345.bsky.social'.  The password will be provided in an environment variable.

The Bluesky post should only be sent if there are tickets available.  The post should first include the link to the calendar webpage 'https://museum-tickets.nintendo.com/en/calendar' and then contain only the days with availability.  Make the link a clickable url in the post.

Test scenarios:
Mock the results of the api call to test the script.  Use the following files to test the script.
calendar_feb.json - tickets available on 28th Feb
calendar_mar.json - no tickets available
calendar_apr.json - no tickets available

