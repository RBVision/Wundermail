import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re
import wunderpy2

#### This is where you call the gmail IMAP server
M = imaplib.IMAP4_SSL('imap.gmail.com', 993)

#### This is where you login to gmail
try:
	M.login('email_here@gmail.com', getpass.getpass('Password: '))
except imaplib.IMAP4.error:
	print "LOGIN FAILED!!!!"

api = wunderpy2.WunderApi()
client = api.get_client('access_token', 'client_id')

##### This is where you list all the available mailboxes in gmail
rv, mailboxes = M.list()
if rv == 'OK':
	print "Mailboxes:"
	print mailboxes

def process_mailbox(M): 
	rv, data = M.search(None, '(ALL)', '(FROM search_for_sender@gmail.com)')
	if rv != 'OK':
		print "ERROR getting message", num
		return

#### Here you define which data you want to fetch
	for num in data[0].split():
		rv, data = M.fetch(num, '(UID BODY.PEEK[TEXT])')
		if rv != 'OK':
			print "ERROR getting message", num
			return

#### This parses email data 
		msg_string = data[0][1]
		msg = email.message_from_string(msg_string)
		if msg.get_content_maintype() == 'multipart':
			for part in msg.walk():
				if part.get_content_type() == "text/plain":
					body = part.get_payload(decode=True)
				else:
					continue


		print "----------"
#### This if statement finds the payment amount			
		if bool(re.search(r'pay|(\d{2},\d{2})|(\d{3},\d{2})', msg_string)) == True: # Enter regular expression(s) here
			payment = re.search(r'pay|(\d{2},\d{2}|(\d{3},\d{2}))', msg_string).group(1) # Enter regular expression(s) here
			print "Payment found: %s EUR" % payment
		else:
			print "No expression found\n"

#### This if statement finds the payment due date
		if bool(re.search(r'(\d{2})\s(January|Februari|March|April|May|June|July|August|September|October|November|December)\s(\d{4})', msg_string)) == True:
			payment_date = re.search(r'(\d{2})\s(January|Februari|March|April|May|June|July|August|September|October|November|December)\s(\d{4})', msg_string)

			day = payment_date.group(1)
			month = payment_date.group(2)
			year = payment_date.group(3)

			print "Payment due date found: %s" % day, month, year
		else:
			print "No payment due date found\n"

#### This creates a task in Wunderlist for each instance of M		
		lists = client.get_lists()
		lists = lists[10]
		# print lists

		task = client.create_task(' ', (" ")) # Enter list_id and task name

rv, data = M.select("INBOX")
if rv == 'OK':
	print "Processing mailbox...\n"
	process_mailbox(M)
	print "----------\n"
	M.close

M.logout
