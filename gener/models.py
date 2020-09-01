from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db import models

class DataSchema(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	col_sep = models.CharField(max_length=50, default=',')
	str_chr = models.CharField(max_length=50, default='"')
	date_created = models.DateTimeField(default=now)
	columns = ArrayField(ArrayField(models.CharField(max_length=200)))

class DataSet(models.Model):
	schema = models.ForeignKey(DataSchema, on_delete=models.CASCADE)
	date_created = models.DateTimeField(default=now)
	num_rows = models.IntegerField()
	task_id = models.CharField(max_length=200, default='someid')