from string import Template

from odpe_management.models import Employee
employee_types = {
    'EMPLOYEE_TYPE_ADMINISTRATOR': 'Admin',
    'EMPLOYEE_TYPE_NORMAL': 'Normal'
}


def get_employee_details(user):
    first_name = Employee.objects.values_list('user__first_name', flat=True).filter(user=user).first()
    last_name = Employee.objects.values_list('user__last_name', flat=True).filter(user=user).first()
    _type = Employee.objects.values_list('type', flat=True).filter(user=user).first()
    return {
        'emp_username': user.username, 'emp_first_name': first_name, 'emp_last_name': last_name,
        'emp_type': _type
    }


def get_common_data_for_ui(user, title='ODPE Management System', add_support_for_data_tables=False):
    context = get_employee_details(user)
    context.update({'page_title': title})
    context.update({'add_data_table_support': add_support_for_data_tables})
    context.update(employee_types)
    return context


def read_template(filename='static/odpe_management/assets/otp_mail_template.txt'):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)
