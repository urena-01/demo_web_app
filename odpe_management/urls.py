from django.urls import path

from odpe_management import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_user, name='login'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('logout', views.logout_user, name='logout'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('employees', views.employees, name='employees'),
    path('add_employee', views.add_employee, name='add_employee'),
    path('edit_employee/<_id>', views.edit_employee, name='edit_employee'),
    path('companies', views.companies, name='companies'),
    path('add_company', views.add_company, name='add_company'),
    path('edit_company/<_id>', views.edit_company, name='edit_company'),
    path('job_types', views.job_types, name='job_types'),
    path('edit_job_type/<_id>', views.edit_job_type, name='edit_job_type'),
    path('add_job_type', views.add_job_type, name='add_job_type'),
    path('ranks', views.ranks, name='ranks'),
    path('add_rank', views.add_rank, name='add_rank'),
    path('edit_rank/<_id>', views.edit_rank, name='edit_rank'),
    path('agencies', views.agencies, name='agencies'),
    path('add_agency', views.add_agency, name='add_agency'),
    path('edit_agency/<_id>', views.edit_agency, name='edit_agency'),
    path('troops', views.troops, name='troops'),
    path('add_troop', views.add_troop, name='add_troop'),
    path('edit_troop/<_id>', views.edit_troop, name='edit_troop'),
    path('jobs', views.jobs, name='jobs'),
    path('my_jobs', views.my_jobs, name='my_jobs'),
    path('add_job', views.add_job, name='add_job'),
    path('generate_invoice', views.generate_invoice, name='generate_invoice'),
    path('view_invoice/<_id>/<_action>', views.view_invoice, name='view_invoice')
]
