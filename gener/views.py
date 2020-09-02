from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .models import DataSchema,DataSet
from . import tasks
import datetime
import sys
import os


def log_in(request,methods=["POST"]):
	if request.method=="POST":
		user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
		print(user)
		if user is not None:
			login(request,user)
			print("Logged in")
			return redirect('index')
		else:
			print("User not exist")
			return render(request,'login.html',{'errors':["No such user"]})
	return render(request,'login.html',{'errors':[]})

def register(request,methods=["POST"]):
	if request.method=="POST":
		if User.objects.filter(username=request.POST.get('username')):
			return render(request,'register.html',{'errors':["User with this username already exists"]})
		user = User.objects.create_user(request.POST.get('username'), request.POST.get('mail'), request.POST.get('password'))
		return redirect('log_in')
	return render(request,'register.html',{'errors':[]})

def logout(request):
	django_logout(request)
	return redirect('log_in')

def index(request):
	if not request.user.is_authenticated:
		return redirect('log_in')
	schemas = DataSchema.objects.filter(user=request.user)
	if not schemas:
		schemas=None
	print(schemas)
	json={'schemas':schemas}
	return render(request, 'main.html',json)


def new_schema(request, methods=["POST"]):
	if request.method=="POST":

		print(request.POST)
		columns = []
		for index in range(len(request.POST.getlist('col_name'))):
			column = [request.POST.getlist('col_name')[index],
			request.POST.getlist('col_type')[index],
			request.POST.getlist('col_from')[index],
			request.POST.getlist('col_to')[index]]
			columns.append(column)
		print(columns)
		try:
			DataSchema.objects.create(
				user=request.user,
				name=request.POST.get('name'),
				col_sep=request.POST.get('col_sep'),
				str_chr=request.POST.get('str_chr'),
				columns=columns,
				#date_created=datetime.datetime.now
				)
		except Exception as e:
			print(e)
			print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
			return redirect('new_schema')
		return redirect('index')
	return render(request,'new_schema.html',{

		})

def new_column(request):
	params = {'col_name':request.GET.get('name'),
	'col_type':request.GET.get('type'),
	'col_from':request.GET.get('from'),
	'col_to':request.GET.get('to'),}
	return render(request,'new_column.html',
		{'col_types':['Full name','Job',"Email", 'Domain name', 'Phone number', 'Company name','Text','Integer','Address','Date'],
		'params':params}

		)

def edit_schema(request, id):
	schema = DataSchema.objects.get(id=id)
	if request.method=="POST":
		print(request.POST)
		columns = []
		for index in range(len(request.POST.getlist('col_name'))):
			column = [request.POST.getlist('col_name')[index],
			request.POST.getlist('col_type')[index],
			request.POST.getlist('col_from')[index],
			request.POST.getlist('col_to')[index]]
			columns.append(column)
		print(columns)
		schema.name=request.POST.get('name')
		schema.col_sep=request.POST.get('col_sep')
		schema.str_chr=request.POST.get('str_chr')
		schema.columns=columns
		try:
			schema.save()
			return redirect('index')
		except Exception as e:
			return render(request,'new_schema.html',{
				'existing_schema':schema,
				'errors':[f'Error editing page: {e}']
				})
	return render(request,'new_schema.html',{
		'existing_schema':schema
		})

def delete_schema(request,id):
	schema = DataSchema.objects.get(id=id)
	schema.delete()
	return redirect('index')

def view_schema(request,id):
	schema = DataSchema.objects.get(id=id)
	sets = DataSet.objects.filter(schema=schema)
	return render(request,'datasets.html',{
		'schema':schema,
		'datasets':sets,
		})

def generate_set(request,id,methods=["POST"]):
	if request.method=="POST":
		schema = DataSchema.objects.get(id=id)
		special_types=['Integer','Text']
		types_to_send = []
		for column in schema.columns:
			if column[1] in special_types:
				types_to_send.append({'type':column[1],'from':int(column[2]),'to':int(column[3])})
			else:
				types_to_send.append(column[1])
		params = {'types':types_to_send,'col_sep':schema.col_sep,'str_chr':schema.str_chr}
		new_data_set = DataSet.objects.create(
			schema=schema,
			num_rows=request.POST['rows_count']
			)
		task = tasks.create_file.delay(params,request.POST['rows_count'],new_data_set.id)
		new_data_set.task_id = task.id
		new_data_set.save()
	return redirect('view_schema', id=id)

from celery.result import AsyncResult
def check_status(request):
	task_id = request.GET.get('task_id')
	res = AsyncResult(task_id)
	res.ready()
	print('res=',res,res.status)
	return render(request,'status_badge.html',{
		'status':res.status
		})



def download(request, filename):
	if default_storage.exists(f'{filename}'):
		print('exists')
		file = default_storage.open(f'{filename}','r')
		response = HttpResponse(file, content_type="text/csv")
		response['Content-Disposition'] = 'attachment; filename=' + f'{filename}.csv'
		file.close()
		return response
	print("error")
	raise Http404

from django.template.defaulttags import register as reg_fil

@reg_fil.filter
def get_range(value):
	return range(value)





