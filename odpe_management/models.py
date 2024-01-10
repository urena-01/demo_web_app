from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Rank(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='Active')


class Agency(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='Active')


class Troop(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='Active')


class Employee(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    troop = models.ForeignKey(Troop, on_delete=models.CASCADE)
    contact = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.IntegerField()
    type = models.CharField(max_length=25, default='Normal')
    status = models.CharField(max_length=20, default='Active')


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default='Active')


class JobType(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Active')


class Invoice(models.Model):
    created_on = models.DateTimeField()
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    

class Job(models.Model):
    performed_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    detail = models.ForeignKey(JobType, on_delete=models.CASCADE)
    post = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    comments = models.CharField(max_length=500, blank=True, null=True)
    hours = models.CharField(max_length=10, blank=True, null=True)
    pay_rate = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    pay = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    pay_status = models.CharField(max_length=10, default='billing')
    submitted_on = models.DateTimeField()
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Active')


class InvoiceItems(models.Model):
    invoice = models.ForeignKey(Invoice, unique=False, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, unique=True, on_delete=models.CASCADE)
