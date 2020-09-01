import requests
import json
import random
import time
from celery import shared_task
import csv
from django.http import HttpResponse
from cachecontrol import CacheControl


def random_string_generator(fr,to):
	lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
	words = lorem.split(' ')
	count = random.randint(fr,to)
	gen_string = ''
	for i in range(count):
		gen_string+=random.choice(words)+' '
	return gen_string

def random_int_generator(fr,to):
	return random.randint(fr,to)



def generate(types,col_sep,str_chr,fake_user_agent='Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'):
	Types = {
	'Full name':'name',
	'Job':'company',
	'Email':'full_email',
	'Domain name':'domain',
	'Phone number':'phone_h',
	'Company name':'company',
	'Address':'address',
	'Date':'birth_data'
	}
	url = 'https://api.namefake.com/random/random'
	
	with requests.Session() as s:
		cached_s = CacheControl(s)
		headers = { 'User-Agent': fake_user_agent}
		raw = cached_s.get(url,headers=headers,timeout=10)
		json_data = json.loads(raw.text)
		json_data['full_email']=json_data['email_u']+'@'+json_data['email_d']
	
	'''
	http = httplib2.Http()
	content = http.request(url)[1]
	json_data = json.loads(content.decode())
	json_data['full_email']=json_data['email_u']+'@'+json_data['email_d']
	#print(json_data)
	'''
	data_string = ''
	for index,item in enumerate(types):
		if type(item) is dict:
			if item['type']=='Integer':
				data_string+=str(random_int_generator(item['from'],item['to']))
			elif item['type']=="Text":
				data_string+=str_chr+random_string_generator(item['from'],item['to'])+str_chr
			else:
				data_string+='UNDEFINED TYPE'
		else:
			elem = Types[item]
			data_string+=json_data[elem]
		if index<len(types)-1:
			data_string+=col_sep
	return data_string,json_data['useragent']

@shared_task
def create_file(params,rows_count,filename):
	'''
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="datasets/{filename}.csv"'
	writer = csv.writer(response)
	for row in range(int(rows_count)):
		writer.writerow(generate(params['types'],params['col_sep'],params['str_chr']))
	return response
	'''
	strings = []
	heading = ""
	for index,par_type in enumerate(params['types']):
		if type(par_type) is dict:
			heading+=par_type['type']
		else:
			heading+=par_type
		if index<len(params['types'])-1:
			heading+=params['col_sep']
	
	new_user_agent = 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
	row = 0
	while row<int(rows_count):
		try:
			result = generate(params['types'],params['col_sep'],params['str_chr'],new_user_agent)
			row+=1
		except Exception as e:
			print(e)
			continue
		string = result[0]
		new_user_agent = result[1]
		if row<int(rows_count)-1:
			string+='\n'
		strings.append(string)
	with open(f'datasets/{filename}.csv', 'w') as f:
		f.write(heading+'\n')
		for string in strings:
			f.write(str(string))
	return strings
	


