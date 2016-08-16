'''
Script to spider specified web page(s) looking for href/src values 
that do not return successfully.

Defense: Validate external references/resources
Offence: Identify resource that may be hijacked/zombified
'''
__author__ = "Benjamin"
__copyright__ = "Copyright 2016, Hivemind"
__license__ = "GPL"
__version__ = "1.0"

import re
import time
import argparse
import requests
from requests.exceptions import ConnectionError # Because importing the whole thing doesn't work?
from urlparse import urlparse
from bs4 import BeautifulSoup

links = {}

# Display status code for external resources
def check_resource(link, host, allResults):
	url = urlparse(link)
	if(url.netloc > '' and url.netloc != host):
		# Skip check if we have already retrieved the link
		if(link in links):
			return

		try:
			r = requests.get(link)
		except requests.exceptions.SSLError as ssle:
			print('[-] Invalid certificate: %s' % link)
			links[link] = 526
			
		except ConnectionError as exc:
			print('[-] Server not found: %s - %s' % (link, exc))
			links[link] = 666
		else:
			try:
				r.raise_for_status()
			except Exception as excp:
				# print('[-] Problem: %s - %s' % (link, excp))
				pass
			links[link] = r.status_code

def show_results(allResults):
	print('-'*80)
	for link in sorted(links, key=links.__getitem__):
		if(allResults == 1 
			or (allResults == 0 and links[link] != 200)
			or (allResults == 4 and links[link] in [404, 410, 666])
		):
			print('%d, %s' % (links[link], link))

def get_parser():
	parser = argparse.ArgumentParser(description='Check external resources of a page to look for resources that are no longer active')
	parser.add_argument("urls", nargs='*', help='Page(s) to spider')
	parser.add_argument('-e', '--error', 
		help='Show only candiate pages; hide 200\'s (Default: false)',
		action='store_true')
	parser.add_argument('-m', '--missing', 
		help='Show only missing pages (404/410\'s) (Default: false)',
		action='store_true')
	parser.add_argument('-s', '--src', 
		help='Do NOT check SRC values (Default: false)', 
		action='store_false')
	parser.add_argument('-a', '--href', 
		help='Check HREF resources (<a href="?") (Default: false)',
		action='store_false')
	parser.add_argument('-v', '--version',
		help='Displays the current version of linkerator',
		action='store_true')

	return parser

def main():
	allResults = 1

	parser = get_parser()
	args = vars(parser.parse_args())

	if args['version']:
		print('Version: %s', __version__)
		return

	if args['missing']:
		print('[+] Showing only 404/410\'s')
		allResults = 4
	elif args['error']:
		print('[+] Omitting result code 200\'s')
		allResults = 0

	if(args['urls']):
		for url in args['urls']:
			# Prefix HTTP if it was not specified
			if(url.find('htt') == -1):
				url = 'http://' + url

			urlBase = urlparse(url)
			print('[+] Checking: ' + urlBase.geturl())
			print('[+] Performed on: ' + time.strftime("%c"))

			try:
				base = requests.get(urlBase.geturl()).text
			except ConnectionError as exc:
				print('[-] Source server not found: %s ' % urlBase.geturl())
				continue
			
			# Complete lazy external references
			# base = base.replace(r'src="//', r'src="http://')
			# base = base.replace(r"src='//", r"src='http://")
			base = re.sub(r'src\s?=\s?\'//', r"src='http://", base)
			base = re.sub(r'src\s?=\s?\"//', r'src="http://', base)
			
			soup = BeautifulSoup(base, 'html.parser') 

			# Check external links
			if(args['href'] == False):
				links = soup.find_all(href=True)

				print('[+] Number of HREFs: %d' % len(links))

				for link in links:
					check_resource(
						link['href'],
						urlBase.netloc,
						allResults
					)

			# Check external sources/scripts
			if(args['src'] == True):
				links = soup.findAll(src=True)
				print('[+] Number of SRCs: %d' % len(links))

				for link in links:
					check_resource(
						link['src'],
						urlBase.netloc,
						allResults
					)
	else:
		print('[+] No action specified. Displaying help')
		parser.print_help()

	show_results(allResults)

if __name__ == '__main__':
    main()
