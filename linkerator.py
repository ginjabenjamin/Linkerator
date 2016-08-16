'''
Script to spider specified web page(s) looking for HREF/SRC values 
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
from urlparse import urlparse
from bs4 import BeautifulSoup

# Display status code for external resources
def check_resource(link, host, allResults):
	url = urlparse(link)
	if(url.netloc > '' and url.netloc != host):
		r = requests.get(link)
		if(r.status_code != 200 or allResults):
			print(r.status_code, link)

def get_parser():
	parser = argparse.ArgumentParser(description='Check external resources of a page to look for resources that are no longer active')
	parser.add_argument("urls", nargs='*', help='Page(s) to spider')
	parser.add_argument('-e', '--error', 
		help='Show only candiate pages; hide 200\'s (Default: false)',
		action='store_true')
	parser.add_argument('-s', '--src', 
		help='Do not check SRC values (Default: false)', 
		action='store_false')
	parser.add_argument('-a', '--href', 
		help='Do not check link HREFs (<a href="?") (Default: false)',
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

	if args['error']:
		print('[+] Omitting result code 200\'s')
		allResults = 0

	if(args['urls']):
		for url in args['urls']:
			urlBase = urlparse(url)
			print('[+] Checking: ' + urlBase.geturl())
			print('[+] Performed on: ' + time.strftime("%c"))
			base = requests.get(urlBase.geturl()).text
			
			# Complete lazy external references
			base = base.replace(r'src="//', r'src="http://')
			base = base.replace(r"src='//", r"src=1http://")
			
			soup = BeautifulSoup(base, 'html.parser') 

			# Check external links
			if(args['href'] == True):
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


if __name__ == '__main__':
    main()

