import random
from datetime import datetime

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core import serializers
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.template.defaulttags import comment
from mailjet_rest import Client

from odpe_management import helpers
from odpe_management.forms import UserForm
from odpe_management.helpers import get_common_data_for_ui, employee_types
from odpe_management.models import Employee, Company, JobType, Rank, Agency, Troop, Job, Invoice, InvoiceItems


# Create your views here.
def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                employee_data = Employee.objects.filter(user=user).first()
                if employee_data.status == 'Active':
                    login(request, user)
                    return redirect('index')
                else:
                    return render(
                        request, 'odpe_management/login.html', {'error_message': 'Your account has been disabled'}
                    )
            else:
                return render(
                    request, 'odpe_management/login.html', {'error_message': 'Your account has been disabled'}
                )
        else:
            return render(request, 'odpe_management/login.html', {'error_message': 'Invalid login'})

    context = {'page_title': 'Login'}
    return render(request, 'odpe_management/login.html', context)


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('login')

    logout(request)
    form = UserForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Logout'
    }
    return render(request, 'odpe_management/logout.html', context)


@transaction.atomic
def forgot_password(request):
    if request.method == "POST":
        action = request.POST['action']
        email = request.POST['email']
        if action == 'send_otp':
            otp = random.randint(1000, 9999)

            message_template = helpers.read_template()
            # add in the actual otp to the message template
            message = message_template.substitute(OTP=otp)

            api_key = '11fb580759258659eda94d9da9c862e5'
            api_secret = 'c6751eb939ec46334fbeb110ab82639d'
            mailjet = Client(auth=(api_key, api_secret), version='v3.1')
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": "noreply@inocentum.tk",
                            "Name": "Urena & Associates LLC."
                        },
                        "To": [
                            {
                                "Email": email,
                                "Name": "User"
                            }
                        ],
                        "Subject": "Urena & Associates LLC. - Password change request!",
                        "TextPart": message,
                        "HTMLPart": "",
                        "CustomID": str(otp)
                    }
                ]
            }
            result = mailjet.send.create(data=data)
            if result.json()['Messages'][0]['Status'] == 'success':
                return HttpResponse('Success::%d' % otp)
            else:
                return HttpResponse(result)
        elif action == 'change_password':
            new_password = request.POST['new_password']

            was_success = True
            message = ''
            sid = transaction.savepoint()
            if was_success:
                # noinspection PyBroadException
                try:
                    user = Employee.objects.filter(user__email=email).first().user
                    user.set_password(new_password)
                    user.save()
                except Exception as ex:
                    was_success, message = False, ex

            if was_success:
                transaction.savepoint_commit(sid)
                return HttpResponse("Success::Password changed successfully. Login again with new password.")
            else:
                # noinspection PyBroadException
                try:
                    transaction.savepoint_rollback(sid)
                except Exception:
                    pass
                return HttpResponse("%s | Unable to change password. Please try again." % message)
    
    context = {'page_title': 'Forgot Password?'}
    return render(request, 'odpe_management/forgot_password.html', context)


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    current_employee = Employee.objects.filter(user=request.user).first()
    
    if current_employee.type == employee_types['EMPLOYEE_TYPE_ADMINISTRATOR']:
        return redirect('jobs')
    else:
        return redirect('my_jobs')

    # context = {}
    # context.update(get_common_data_for_ui(request.user, 'Dashboard'))
    # return render(request, 'odpe_management/index.html', context)


@transaction.atomic
def my_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    current_employee = Employee.objects.filter(user=request.user).first()

    if request.method == "POST":
        action = request.POST['action']

        if action == 'change_password':
            current_password = request.POST['current_password']
            new_password = request.POST['new_password']
            if request.user.check_password(current_password):
                was_success = True
                message = ''
                sid = transaction.savepoint()
                if was_success:
                    # noinspection PyBroadException
                    try:
                        request.user.set_password(new_password)
                        request.user.save()
                    except Exception as ex:
                        was_success, message = False, ex

                if was_success:
                    transaction.savepoint_commit(sid)
                    return HttpResponse("Success::Password changed successfully. Login again with new password.")
                else:
                    # noinspection PyBroadException
                    try:
                        transaction.savepoint_rollback(sid)
                    except Exception:
                        pass
                    return HttpResponse("%s | Unable to change password. Please try again." % message)
            else:
                return HttpResponse("Old Password did not matched. Please enter properly.")

    context = {'employee': current_employee}
    context.update(get_common_data_for_ui(request.user, title='My Profile'))

    return render(request, 'odpe_management/my_profile.html', context)


def employees(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_employees = Employee.objects.all()
    context = {'all_employees': all_employees}
    context.update(get_common_data_for_ui(request.user, 'Employees'))
    return render(request, 'odpe_management/employee.html', context)


@transaction.atomic
def add_employee(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        contact = request.POST['contact']
        permanent_id = request.POST['permanent_id']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        _type = request.POST['type']
        rank_id = request.POST['rank_id']
        agency_id = request.POST['agency_id']
        troop_id = request.POST['troop_id']
        zip_code = request.POST['zip_code']

        a_rank = Rank.objects.filter(id=rank_id).first()
        an_agency = Agency.objects.filter(id=agency_id).first()
        a_troop = Troop.objects.filter(id=troop_id).first()

        was_success = True
        message = ''
        sid = transaction.savepoint()

        if was_success:
            try:
                new_user = User.objects.create_user(
                    username=permanent_id, email=email, password=password
                )
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()
            except Exception as ex:
                was_success, message = False, ex
        
        if was_success:
            try:
                new_employee = Employee(
                    user=new_user, rank=a_rank, agency=an_agency, troop=a_troop, contact=contact, address=address,
                    city=city, state=state, zip=zip_code, type=_type
                )
                new_employee.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    all_ranks = Rank.objects.filter(status='Active').all()
    all_agencies = Agency.objects.filter(status='Active').all()
    all_troops = Troop.objects.filter(status='Active').all()
    context = {
        'all_ranks': all_ranks, 'all_agencies': all_agencies, 'all_troops': all_troops
    }

    context.update(get_common_data_for_ui(request.user, 'Add Employee'))
    return render(request, 'odpe_management/add_employee.html', context)


@transaction.atomic
def edit_employee(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        _type = request.POST['type']
        rank_id = request.POST['rank_id']
        agency_id = request.POST['agency_id']
        troop_id = request.POST['troop_id']
        zip_code = request.POST['zip_code']

        a_rank = Rank.objects.filter(id=rank_id).first()
        an_agency = Agency.objects.filter(id=agency_id).first()
        a_troop = Troop.objects.filter(id=troop_id).first()

        was_success = True
        message = ''
        sid = transaction.savepoint()
        
        if was_success:
            try:
                current_employee = Employee.objects.filter(id=_id).first()
                current_employee.contact = contact
                current_employee.address = address
                current_employee.city = city
                current_employee.state = state
                current_employee.rank = a_rank
                current_employee.agency = an_agency
                current_employee.troop = a_troop
                current_employee.zip = zip_code
                current_employee.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            try:
                current_user = current_employee.user
                current_user.first_name = first_name
                current_user.last_name = last_name
                current_user.email = email
                current_user.save()
            except Exception as ex:
                was_success, message = False, ex
        
        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse('Success')
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_employee = Employee.objects.filter(id=_id).first()
    all_ranks = Rank.objects.filter(status='Active').all()
    all_troops = Troop.objects.filter(status='Active').all()
    all_agencies = Agency.objects.filter(status='Active').all()
    context = {
        'all_ranks': all_ranks, 'current_employee': current_employee, 'all_troops': all_troops,
        'all_agencies': all_agencies
    }
    context.update(get_common_data_for_ui(request.user, 'Edit employee'))
    return render(request, 'odpe_management/edit_employee.html', context)


def companies(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_companies = Company.objects.all()
    context = {'all_companies': all_companies}
    context.update(get_common_data_for_ui(request.user, 'Companies'))
    return render(request, 'odpe_management/company.html', context)


@transaction.atomic
def add_company(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        company_name = request.POST['company_name']

        was_success = True
        message = ''
        sid = transaction.savepoint()

        if was_success:
            try:
                new_company = Company(name=company_name)
                new_company.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    context = {}
    context.update(get_common_data_for_ui(request.user, 'Add Company'))
    return render(request, 'odpe_management/add_company.html', context)


@transaction.atomic
def edit_company(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        company_name = request.POST['company_name']
        company_status = request.POST['company_status']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                current_company = Rank.objects.filter(id=_id).first()
                current_company.name = company_name
                current_company.status = company_status
                current_company.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_company = Company.objects.filter(id=_id).first()

    context = {}
    context.update({'current_company': current_company})
    context.update(get_common_data_for_ui(request.user, 'Edit Company'))
    return render(request, 'odpe_management/edit_company.html', context)


def job_types(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_job_types = JobType.objects.all()
    context = {'all_job_types': all_job_types}
    context.update(get_common_data_for_ui(request.user, 'Job Types'))
    return render(request, 'odpe_management/job_type.html', context)


@transaction.atomic
def add_job_type(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        company_id = request.POST['company_id']
        name = request.POST['name']
        rate = request.POST['rate']

        a_company = Company.objects.filter(id=company_id).first()

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                new_job_type = JobType(company=a_company, name=name, rate=rate)
                new_job_type.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    all_companies = Company.objects.filter(status='Active').all()
    context = {'all_companies': all_companies}
    context.update(get_common_data_for_ui(request.user, 'Add Job Type'))
    return render(request, 'odpe_management/add_job_type.html', context)


@transaction.atomic
def edit_job_type(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        company_id = request.POST['company_id']
        name = request.POST['name']
        rate = request.POST['rate']
        status = request.POST['job_type_status']

        a_company = Company.objects.filter(id=company_id).first()

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                current_job_type = JobType.objects.filter(id=_id).first()
                current_job_type.company = a_company
                current_job_type.name = name
                current_job_type.rate = rate
                current_job_type.status = status
                current_job_type.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_job_type = JobType.objects.filter(id=_id).first()
    all_companies = Company.objects.filter(status='Active').all()
    context = {'all_companies': all_companies, 'current_job_type': current_job_type}
    context.update(get_common_data_for_ui(request.user, 'Edit Job Type'))
    return render(request, 'odpe_management/edit_job_type.html', context)


def ranks(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_ranks = Rank.objects.all()
    context = {'all_ranks': all_ranks}
    context.update(get_common_data_for_ui(request.user, 'Ranks'))
    return render(request, 'odpe_management/rank.html', context)


@transaction.atomic
def add_rank(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        rank_name = request.POST['rank_name']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                new_rank = Rank(name=rank_name)
                new_rank.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    context = {}
    context.update(get_common_data_for_ui(request.user, 'Add Rank'))
    return render(request, 'odpe_management/add_rank.html', context)


@transaction.atomic
def edit_rank(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        rank_name = request.POST['rank_name']
        rank_status = request.POST['rank_status']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                current_rank = Rank.objects.filter(id=_id).first()
                current_rank.name = rank_name
                current_rank.status = rank_status
                current_rank.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_rank = Rank.objects.filter(id=_id).first()

    context = {}
    context.update({'current_rank': current_rank})
    context.update(get_common_data_for_ui(request.user, 'Edit Rank'))
    return render(request, 'odpe_management/edit_rank.html', context)


def agencies(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_agencies = Agency.objects.all()
    context = {'all_agencies': all_agencies}
    context.update(get_common_data_for_ui(request.user, 'Agencies'))
    return render(request, 'odpe_management/agency.html', context)


@transaction.atomic
def add_agency(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        agency_name = request.POST['agency_name']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                new_agency = Agency(name=agency_name)
                new_agency.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    context = {}
    context.update(get_common_data_for_ui(request.user, 'Add Agency'))
    return render(request, 'odpe_management/add_agency.html', context)


@transaction.atomic
def edit_agency(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        agency_name = request.POST['agency_name']
        agency_status = request.POST['agency_status']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                current_agency = Agency.objects.filter(id=_id).first()
                current_agency.name = agency_name
                current_agency.status = agency_status
                current_agency.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_agency = Agency.objects.filter(id=_id).first()
    context = {}
    context.update({'current_agency': current_agency})
    context.update(get_common_data_for_ui(request.user, 'Edit Agency'))
    return render(request, 'odpe_management/edit_agency.html', context)


def troops(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_troops = Troop.objects.all()
    context = {'all_troops': all_troops}
    context.update(get_common_data_for_ui(request.user, 'Troops'))
    return render(request, 'odpe_management/troop.html', context)


@transaction.atomic
def add_troop(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        troop_name = request.POST['troop_name']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                new_troop = Troop(name=troop_name)
                new_troop.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    context = {}
    context.update(get_common_data_for_ui(request.user, 'Add Troop'))
    return render(request, 'odpe_management/add_troop.html', context)


@transaction.atomic
def edit_troop(request, _id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        troop_name = request.POST['troop_name']
        troop_status = request.POST['troop_status']

        was_success = True
        message = ''
        sid = transaction.savepoint()
        if was_success:
            try:
                current_troop = Troop.objects.filter(id=_id).first()
                current_troop.name = troop_name
                current_troop.status = troop_status
                current_troop.save()
            except Exception as ex:
                was_success, message = False, ex

        if was_success:
            transaction.savepoint_commit(sid)
            return HttpResponse("Success")
        else:
            # noinspection PyBroadException
            try:
                transaction.savepoint_rollback(sid)
            except Exception:
                pass
            return HttpResponse(message)

    current_troop = Troop.objects.filter(id=_id).first()
    context = {}
    context.update({'current_troop': current_troop})
    context.update(get_common_data_for_ui(request.user, 'Edit Troop'))
    return render(request, 'odpe_management/edit_troop.html', context)


def jobs(request):
    if not request.user.is_authenticated:
        return redirect('login')

    all_jobs = Job.objects.all()
    context = {'all_jobs': all_jobs}
    context.update(get_common_data_for_ui(request.user, 'All Jobs'))
    return render(request, 'odpe_management/job.html', context)


def my_jobs(request):
    if not request.user.is_authenticated:
        return redirect('login')

    employee = Employee.objects.filter(user=request.user).first()

    my_jobs_list = Job.objects.filter(performed_by=employee).all()
    context = {'my_jobs_list': my_jobs_list}
    context.update(get_common_data_for_ui(request.user, 'My Jobs'))
    return render(request, 'odpe_management/my_jobs.html', context)


@transaction.atomic
def add_job(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        action = request.POST['action']
        if action == 'get_job_types':
            company_id = request.POST['company_id']
            company = Company.objects.filter(id=company_id).first()
            all_job_types = JobType.objects.filter(company=company).all()
            all_job_types = serializers.serialize('json', all_job_types)
            return HttpResponse(all_job_types, content_type='application/json')
        elif action == 'add_new_job':
            ids = ["company_id", "job_types", "post", "start_date", "start_time", "end_date", "end_time", "comment"]
            values = dict()

            for an_id in ids:
                values.update({an_id: request.POST[an_id]})

            start_date_time = values['start_date'] + 'T' + values['start_time']
            end_date_time = values['end_date'] + 'T' + values['end_time']

            performed_by = Employee.objects.filter(user=request.user).first()
            company = Company.objects.filter(id=values['company_id']).first()
            job_type = JobType.objects.filter(id=values['job_types']).first()

            start_date = datetime.strptime(start_date_time, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_time, '%Y-%m-%dT%H:%M')
            diff_between_dates = end_date - start_date
            days, seconds = diff_between_dates.days, diff_between_dates.seconds
            hours_worked = days * 24 + seconds / 3600

            if hours_worked < 0:
                return HttpResponse(
                    'Please select Start DateTime and End DateTime correctly. End DateTime cannot be lower than Start DateTime')
            else:
                was_success = True
                message = ''
                sid = transaction.savepoint()
                if was_success:
                    try:
                        new_job = Job(
                            performed_by=performed_by, company=company, detail=job_type, post=values['post'],
                            start_date=start_date, end_date=end_date, comments=comment, hours=hours_worked,
                            pay_rate=job_type.rate, pay=float(job_type.rate) * hours_worked, submitted_on=datetime.now()
                        )
                        new_job.save()
                    except Exception as ex:
                        was_success, message = False, ex
        
                if was_success:
                    transaction.savepoint_commit(sid)
                    return HttpResponse("Success")
                else:
                    # noinspection PyBroadException
                    try:
                        transaction.savepoint_rollback(sid)
                    except Exception:
                        pass
                    return HttpResponse(message)

    all_company = Company.objects.filter(status='Active').all()
    context = {'all_company': all_company}
    context.update(get_common_data_for_ui(request.user, 'Add job'))
    return render(request, 'odpe_management/add_job.html', context)


@transaction.atomic
def generate_invoice(request):
    current_employee = Employee.objects.filter(user=request.user).first()
    job_ids = request.POST['job_ids']

    job_ids = job_ids.split('::')[0:-1]

    all_jobs = Job.objects.filter(id__in=job_ids)

    was_success = True
    message = ''
    sid = transaction.savepoint()
    if was_success:
        try:
            new_invoice = Invoice(created_on=datetime.now(), created_by=current_employee)
            new_invoice.save()
        except Exception as ex:
            was_success, message = False, ex

    for a_job in all_jobs:
        if was_success:
            try:
                temp_invoice_item = InvoiceItems(invoice=new_invoice, job=a_job)
                temp_invoice_item.save()
        
                a_job.invoice = new_invoice
                a_job.pay_status = 'billing'
                a_job.save()
            except Exception as ex:
                was_success, message = False, ex

    if was_success:
        transaction.savepoint_commit(sid)
        return HttpResponse("Success::" + str(new_invoice.id))
    else:
        # noinspection PyBroadException
        try:
            transaction.savepoint_rollback(sid)
        except Exception:
            pass
        return HttpResponse(message)


def view_invoice(request, _id, _action):
    invoice = Invoice.objects.filter(id=_id).first()
    invoice_items = InvoiceItems.objects.filter(invoice=invoice)

    total_hours = 0
    total_pay = 0.00
    for item in invoice_items:
        total_hours += float(item.job.hours)
        total_pay += float(item.job.pay)

    context = {
        'invoice': invoice, 'invoice_items': invoice_items, 'total_jobs': len(invoice_items),
        'total_hours': total_hours, 'total_pay': format(total_pay, '.2f'), 'action': _action
    }
    return render(request, 'odpe_management/invoice.html', context)
