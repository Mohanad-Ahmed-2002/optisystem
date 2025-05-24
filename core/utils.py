import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
import os

def render_to_pdf(template_src, context_dict):
    html = render_to_string(template_src, context_dict)

    # تحديد المسار الكامل لـ wkhtmltopdf في Windows
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf = pdfkit.from_string(html, False, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    return response


def is_manager(user):
    return user.is_authenticated and user.role == 'manager'

def is_employee(user):
    return user.is_authenticated and user.role == 'employee'
