from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404
from django.contrib import  messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import  User
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import *
import  razorpay
from .models import Plan, Userprofile,Payment
from django.conf import settings
from django.core.mail  import send_mail
from django.template.loader import render_to_string
import requests
from requests.exceptions import RequestException
import socket
import os
from django.db.models import Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import xlsxwriter
from io import BytesIO
from django.db.models import Count
from reportlab.pdfgen import canvas
from django.core.mail import EmailMultiAlternatives
from reportlab.lib.units import inch

# Create your views here.
# def payment_page(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         amount = request.POST.get("amount")
#         print(name)
#         print(amount)
#         client = razorpay.Client(auth=(""))
        
#     return render(request, 'payment.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect(dashboard)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except :
            messages.error(request, "user name does not exist")

        user = authenticate(request, username=username, password=password)
        
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Incorrect Password")

    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request,"logout successfully" )
    return redirect('login')


@login_required(login_url="login")
def dashboard(request):
    search_qurery = ' '
    if request.GET.get('search_query'):
        search_qurery = request.GET.get('search_query')

    users = Userprofile.objects.filter(user__icontains=search_qurery)
    user = Userprofile.objects.all().order_by('id')
    # Paginate users
    page = request.GET.get('page')
    results = 5
    paginator = Paginator(user, results)
    try:
        user = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        user = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        user = paginator.page(page)

    left = (int(page) -  1)
    if left < 1 :
        left = 1
    right = (int(page) + 2)
    if right > paginator.num_pages:
        right = paginator.num_pages+1
    custom_range = range(left, right)

    # Paginate plans (separate from users)
    plan_page = request.GET.get('plan_page', 1)
    plan_results = 3
    plan_list = Plan.objects.all().order_by('id')
    plan_paginator = Paginator(plan_list, plan_results)
    try:
        paginated_plans = plan_paginator.page(plan_page)
    except PageNotAnInteger:
        paginated_plans = plan_paginator.page(1)
    except EmptyPage:
        paginated_plans = plan_paginator.page(plan_paginator.num_pages)

    plan_left = max(1, int(plan_page) - 1)
    plan_right = min(plan_paginator.num_pages + 1, int(plan_page) + 2)
    plan_custom_range = range(plan_left, plan_right)

    total_plan = plan_list.count()
    u = Userprofile.objects.all()
    total_user = u.count()
    context = {
        'plans': paginated_plans,
        'plan_paginator': plan_paginator,
        'plan_custom_range': plan_custom_range,
        'total_plan': total_plan,
        'users': users,
        'user': user,
        'search_qurery': search_qurery,
        'paginator': paginator,
        'custom_range': custom_range,
        'total_user': total_user
    }
    return render(request,'dashboard.html',context)

@login_required(login_url="login")
def plans(request):
    plan_list = Plan.objects.all().order_by('id')
    page = request.GET.get('page', 1)
    results = 3
    paginator = Paginator(plan_list, results)
    try:
        paginated_plans = paginator.page(page)
    except PageNotAnInteger:
        paginated_plans = paginator.page(1)
    except EmptyPage:
        paginated_plans = paginator.page(paginator.num_pages)

    left = max(1, int(page) - 1)
    right = min(paginator.num_pages + 1, int(page) + 2)
    custom_range = range(left, right)

    context = {
        'plans': paginated_plans,
        'paginator': paginator,
        'custom_range': custom_range
    }
    return render(request, 'plans.html', context)

@login_required(login_url="login")
def create_plan(request):
    if request.method == 'POST':
        form= planform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"plan added successfully")
            return redirect('/')
    else:
        form = planform()
    return render(request,"create-plan.html",{'form':form})

@login_required(login_url="login")
def delete_plan(request,pk):
    if request.method == 'POST':
        pi = Plan.objects.get(id=pk)
        pi.delete()
        messages.warning(request, 'plan deleted successfully')
        return redirect('/')
    else:
        messages.error(request,'Oopse something went wrong!!!')

@login_required(login_url="login")
def update_plan(request,pk):
    pi = Plan.objects.get(id=pk)
    form = planform(instance=pi)
    if request.method == 'POST':
        form =planform(request.POST, instance=pi)
        if form.is_valid():
            form.save()
            messages.info(request,'Plan updated successfully')
            return redirect('/')
    context = {'form':form}



    return render(request,'update-plan.html',context)

@login_required(login_url="login")
def users(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    if search_query:
        user_list = Userprofile.objects.filter(user__icontains=search_query).order_by('id')
    else:
        user_list = Userprofile.objects.all().order_by('id')

    page = request.GET.get('page', 1)
    results = 5
    paginator = Paginator(user_list, results)
    
    try:
        paginated_users = paginator.page(page)
    except PageNotAnInteger:
        paginated_users = paginator.page(1)
    except EmptyPage:
        paginated_users = paginator.page(paginator.num_pages)

    left = max(1, int(page) - 1)
    right = min(paginator.num_pages + 1, int(page) + 2)
    custom_range = range(left, right)

    context = {
        'users': paginated_users,
        'search_query': search_query,
        'paginator': paginator,
        'custom_range': custom_range
    }
    
    return render(request, 'users.html', context)

@login_required(login_url="login")
def create_user(request):
    if request.method == 'POST':
        form = clientform(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Handle profile image upload
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            
            # Handle ID proof upload
            if 'id_proof' in request.FILES:
                user.id_proof = request.FILES['id_proof']
            
            user.save()
            messages.success(request, 'User added successfully')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = clientform()
    
    context = {
        'form': form,
    }
    return render(request, "create-user.html", context)

@login_required(login_url="login")
def edit_user(request, pk):
    try:
        user = Userprofile.objects.get(user=pk)
        form = clientform(instance=user)
        if request.method == 'POST':
            form = clientform(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.info(request, 'User updated successfully')
                return redirect('/users')
        return render(request, 'update-user.html', {'form': form})
    except Userprofile.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('/users')
    except Exception as e:
        messages.error(request, f"Error updating user: {str(e)}")
        return redirect('/users')

@login_required(login_url="login")
def delete_user(request,pk):
    if request.method == 'POST':
        pi = Userprofile.objects.get(pk=pk)
        pi.delete()
        messages.warning(request, 'User deleted successfully')
        return redirect('/users')
    else:
        messages.error(request,"oops something went wrong!!!")



@login_required(login_url="login")
def view_user(request, pk):
    try:
        user = Userprofile.objects.get(user=pk)
        context = {'user': user}
        return render(request, "view-user.html", context)
    except Userprofile.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('/users')
    except Exception as e:
        messages.error(request, f"Error viewing user: {str(e)}")
        return redirect('/users')



def bill(request):
    if request.method == "POST":
        try:
            # Check internet connectivity first
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
            except OSError:
                messages.error(request, "No internet connection. Please check your network.")
                return render(request, "bill.html")

            # Get form data
            name = request.POST.get("name")
            email = request.POST.get("email")
            amount = request.POST.get("amount")

            if not all([name, email, amount]):
                messages.error(request, "Please fill all fields")
                return render(request, "bill.html")

            try:
                amount_in_paise = int(float(amount) * 100)
            except ValueError:
                messages.error(request, "Invalid amount")
                return render(request, "bill.html")

            # Initialize Razorpay client with timeout
            client = razorpay.Client(
                auth=("rzp_test_1tK7yAY7ByvjWB", "NgNapLFu0X7xpCjnJZYlCm4k")
            )

            try:
                # Add timeout to Razorpay API call
                payment = client.order.create({
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'payment_capture': '1'
                })
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as e:
                messages.error(request, 
                    "Unable to connect to payment service. Please try again later.")
                return render(request, "bill.html")

            # Create payment record
            payment_record = Payment(
                name=name,
                email=email,
                amount=float(amount),
                payment_id=payment['id']
            )
            payment_record.save()

            return render(request, "bill.html", {
                'payment': payment,
                'name': name,
                'email': email,
                'amount': float(amount)
            })

        except Exception as e:
            messages.error(request, 
                "Payment service temporarily unavailable. Please try again later.")
            return render(request, "bill.html")

    return render(request, "bill.html")


def success(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            # Validate payment data
            if not all([payment_id, order_id, signature]):
                messages.error(request, "Invalid payment data received")
                return redirect('bill')

            # Get payment record
            try:
                payment = Payment.objects.get(payment_id=order_id)
            except Payment.DoesNotExist:
                messages.error(request, "Payment record not found")
                return redirect('bill')

            # Verify payment signature
            client = razorpay.Client(
                auth=("rzp_test_1tK7yAY7ByvjWB", "NgNapLFu0X7xpCjnJZYlCm4k")
            )
            
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }

            try:
                client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:
                messages.error(request, "Payment verification failed")
                return redirect('bill')

            # Update payment status
            payment.paid = True
            payment.save()

            # Send email confirmation
            try:
                template_path = os.path.join(settings.BASE_DIR, 'plan', 'templates', 'email.html')
                txt_template_path = os.path.join(settings.BASE_DIR, 'plan', 'templates', 'email.txt')
                
                msg_plain = render_to_string(txt_template_path, {'payment': payment})
                msg_html = render_to_string(template_path, {'payment': payment})

                # Generate PDF receipt (modern look)
                pdf_buffer = BytesIO()
                p = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter

                # Header
                p.setFillColor(colors.HexColor('#007bff'))
                p.rect(0, height-80, width, 80, fill=1, stroke=0)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 28)
                p.drawString(40, height-55, "Payment Receipt")
                p.setFont("Helvetica", 12)
                p.drawString(width-200, height-55, payment.created_at.strftime('%Y-%m-%d %H:%M'))

                # Company/Brand
                p.setFillColor(colors.HexColor('#222831'))
                p.setFont("Helvetica-Bold", 16)
                p.drawString(40, height-110, "Swarajya Services")
                p.setFont("Helvetica", 10)
                p.drawString(40, height-125, "Thank you for your payment!")

                # Divider
                p.setStrokeColor(colors.HexColor('#007bff'))
                p.setLineWidth(2)
                p.line(40, height-135, width-40, height-135)

                # Payment Details Section
                p.setFillColor(colors.black)
                p.setFont("Helvetica-Bold", 14)
                p.drawString(40, height-160, "Payment Details")
                p.setFont("Helvetica", 12)
                y = height-185
                details = [
                    ("Name", payment.name),
                    ("Email", payment.email),
                    ("Payment ID", payment.payment_id),
                    ("Amount Paid", f"₹{payment.amount}"),
                    ("Status", "Successful" if payment.paid else "Failed"),
                ]
                for label, value in details:
                    p.setFont("Helvetica-Bold", 12)
                    p.drawString(60, y, f"{label}:")
                    p.setFont("Helvetica", 12)
                    p.drawString(180, y, str(value))
                    y -= 22

                # Divider
                p.setStrokeColor(colors.HexColor('#eeeeee'))
                p.setLineWidth(1)
                p.line(40, y+10, width-40, y+10)
                y -= 20

                # Footer/Thank you
                p.setFont("Helvetica-Oblique", 11)
                p.setFillColor(colors.HexColor('#007bff'))
                p.drawString(40, y, "Thank you for choosing Swarajya Services. For support: 1800-123-4567")
                p.setFillColor(colors.black)
                p.setFont("Helvetica", 9)
                p.drawString(40, y-15, f"© {payment.created_at.year} Swarajya Services. All rights reserved.")

                p.showPage()
                p.save()
                pdf_buffer.seek(0)

                email = EmailMultiAlternatives(
                    subject="🎉 Payment Received Successfully! 🎉",
                    body=msg_plain,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[payment.email],
                )
                email.attach_alternative(msg_html, "text/html")
                email.attach(f"receipt_{payment.payment_id}.pdf", pdf_buffer.read(), "application/pdf")
                email.send(fail_silently=False)
            except Exception as e:
                # Log email error but don't stop the success flow
                print(f"Email sending failed: {str(e)}")
                messages.warning(request, "Payment successful but email could not be sent. Please contact support.")

            messages.success(request, "Payment successful! Confirmation email sent.")
            return render(request, "success.html", {
                'payment': payment,
                'payment_id': payment_id
            })

        except Exception as e:
            messages.error(request, f"Payment processing failed: {str(e)}")
            return redirect('bill')

    return redirect('bill')

def email(request):
    
    return render(request, 'email.html')

def inline_pdf(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and file_path.lower().endswith('.pdf'):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
        return response
    raise Http404("PDF not found")

def blank(request):
    try:
        return render(request, 'blank.html')
    except Exception as e:
        messages.error(request, f"Error accessing page: {str(e)}")
        return redirect('users')

@login_required(login_url="login")
def reports(request):
    return render(request, 'reports.html')

@login_required(login_url="login")
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        format_type = request.POST.get('format')
        
        if format_type == 'pdf':
            return generate_pdf_report(request, report_type)
        else:
            return generate_excel_report(request, report_type)
    
    return redirect('reports')

def generate_pdf_report(request, report_type):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))  # Use landscape orientation
    elements = []
    styles = getSampleStyleSheet()
    
    # Add title and date
    title = Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Add report generation date
    date_style = styles['Normal']
    date_style.alignment = 1  # Center alignment
    date = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
    elements.append(date)
    elements.append(Spacer(1, 20))
    
    if report_type == 'users':
        user_filter = request.POST.get('user_filter', 'all')
        data = [['Name', 'Email', 'Phone', 'Address', 'Status']]
        
        if user_filter == 'active':
            users = Userprofile.objects.filter(is_active=True)
        elif user_filter == 'inactive':
            users = Userprofile.objects.filter(is_active=False)
        else:
            users = Userprofile.objects.all()
            
        for user in users:
            data.append([
                str(user.user),
                str(user.email or ''),
                str(user.phoneno or ''),
                str(user.address or ''),
                'Active' if user.is_active else 'Inactive'
            ])
    
    elif report_type == 'plans':
        plan_filter = request.POST.get('plan_filter', 'all')
        data = [['Plan Name', 'Cost', 'Duration', 'Active Users']]
        
        if plan_filter == 'popular':
            plans = Plan.objects.annotate(user_count=Count('userprofile')).order_by('-user_count')
        else:
            plans = Plan.objects.all()
            
        for plan in plans:
            data.append([
                str(plan.plan_name),
                f"₹{plan.cost}",
                str(plan.Duration),
                str(plan.userprofile_set.count())
            ])
    
    elif report_type == 'payments':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        payment_status = request.POST.get('payment_status', 'all')
        
        data = [['Name', 'Email', 'Amount', 'Payment ID', 'Date', 'Status']]
        payments = Payment.objects.filter(created_at__range=[start_date, end_date])
        
        if payment_status == 'successful':
            payments = payments.filter(paid=True)
        elif payment_status == 'failed':
            payments = payments.filter(paid=False)
            
        for payment in payments:
            data.append([
                str(payment.name),
                str(payment.email),
                f"₹{payment.amount}",
                str(payment.payment_id),
                payment.created_at.strftime('%Y-%m-%d'),
                'Successful' if payment.paid else 'Failed'
            ])
    
    elif report_type == 'revenue_summary':
        data = [['Month', 'Total Revenue', 'Successful Payments', 'Failed Payments']]
        payments = Payment.objects.all().order_by('created_at')
        
        # Group by month
        monthly_data = {}
        for payment in payments:
            month = payment.created_at.strftime('%Y-%m')
            if month not in monthly_data:
                monthly_data[month] = {'revenue': 0, 'successful': 0, 'failed': 0}
            
            if payment.paid:
                monthly_data[month]['revenue'] += payment.amount
                monthly_data[month]['successful'] += 1
            else:
                monthly_data[month]['failed'] += 1
        
        for month, stats in monthly_data.items():
            data.append([
                month,
                f"₹{stats['revenue']}",
                str(stats['successful']),
                str(stats['failed'])
            ])
    
    elif report_type == 'user_summary':
        data = [['Month', 'New Users', 'Active Users', 'Inactive Users']]
        users = Userprofile.objects.all().order_by('start_date')
        
        # Group by month
        monthly_data = {}
        for user in users:
            if user.start_date:  # Only process users with start dates
                month = user.start_date.strftime('%Y-%m')
                if month not in monthly_data:
                    monthly_data[month] = {'new': 0, 'active': 0, 'inactive': 0}
                
                monthly_data[month]['new'] += 1
                if user.is_active:
                    monthly_data[month]['active'] += 1
                else:
                    monthly_data[month]['inactive'] += 1
        
        # Sort months chronologically
        for month in sorted(monthly_data.keys()):
            stats = monthly_data[month]
            data.append([
                month,
                str(stats['new']),
                str(stats['active']),
                str(stats['inactive'])
            ])
    
    elif report_type == 'plan_summary':
        data = [['Plan Name', 'Total Users', 'Active Users', 'Revenue Generated']]
        plans = Plan.objects.all()
        
        for plan in plans:
            users = plan.userprofile_set.all()
            active_users = users.filter(is_active=True)
            
            # Calculate revenue based on plan cost and number of active users
            revenue = plan.cost * active_users.count()
            
            data.append([
                str(plan.plan_name),
                str(users.count()),
                str(active_users.count()),
                f"₹{revenue}"
            ])
    
    # Create table with improved styling
    table = Table(data, repeatRows=1)  # Repeat header on each page
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    return response

def generate_excel_report(request, report_type):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add title and date
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    date_format = workbook.add_format({
        'font_size': 12,
        'align': 'center'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'left'
    })
    
    # Write title
    worksheet.merge_range('A1:E1', f"{report_type.replace('_', ' ').title()} Report", title_format)
    worksheet.merge_range('A2:E2', f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_format)
    
    if report_type == 'users':
        user_filter = request.POST.get('user_filter', 'all')
        headers = ['Name', 'Email', 'Phone', 'Address', 'Status']
        
        if user_filter == 'active':
            users = Userprofile.objects.filter(is_active=True)
        elif user_filter == 'inactive':
            users = Userprofile.objects.filter(is_active=False)
        else:
            users = Userprofile.objects.all()
        
        worksheet.write_row(3, 0, headers, header_format)
        
        for i, user in enumerate(users, start=4):
            worksheet.write_row(i, 0, [
                str(user.user),
                str(user.email),
                str(user.phoneno),
                str(user.address),
                'Active' if user.is_active else 'Inactive'
            ], cell_format)
    
    elif report_type == 'plans':
        plan_filter = request.POST.get('plan_filter', 'all')
        headers = ['Plan Name', 'Cost', 'Duration', 'Active Users']
        
        if plan_filter == 'popular':
            plans = Plan.objects.annotate(user_count=Count('userprofile')).order_by('-user_count')
        else:
            plans = Plan.objects.all()
        
        worksheet.write_row(3, 0, headers, header_format)
        
        for i, plan in enumerate(plans, start=4):
            worksheet.write_row(i, 0, [
                str(plan.plan_name),
                f"₹{plan.cost}",
                str(plan.Duration),
                str(plan.userprofile_set.count())
            ], cell_format)
    
    elif report_type == 'payments':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        payment_status = request.POST.get('payment_status', 'all')
        headers = ['Name', 'Email', 'Amount', 'Payment ID', 'Date', 'Status']
        
        payments = Payment.objects.filter(created_at__range=[start_date, end_date])
        if payment_status == 'successful':
            payments = payments.filter(paid=True)
        elif payment_status == 'failed':
            payments = payments.filter(paid=False)
        
        worksheet.write_row(3, 0, headers, header_format)
        
        for i, payment in enumerate(payments, start=4):
            worksheet.write_row(i, 0, [
                str(payment.name),
                str(payment.email),
                f"₹{payment.amount}",
                str(payment.payment_id),
                payment.created_at.strftime('%Y-%m-%d'),
                'Successful' if payment.paid else 'Failed'
            ], cell_format)
    
    # Adjust column widths
    for i in range(len(headers)):
        worksheet.set_column(i, i, 15)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    return response

@login_required(login_url="login")
def analytics(request):
    # Get total users and active users
    total_users = Userprofile.objects.count()
    active_users = Userprofile.objects.filter(is_active=True).count()
    
    # Calculate revenue
    total_revenue = sum(plan.cost * plan.userprofile_set.filter(is_active=True).count() 
                       for plan in Plan.objects.all())
    
    # Calculate monthly revenue
    current_month = datetime.now().month
    monthly_revenue = sum(plan.cost * plan.userprofile_set.filter(
        is_active=True, start_date__month=current_month).count() 
        for plan in Plan.objects.all())
    
    # Get plan statistics
    total_plans = Plan.objects.count()
    popular_plan = Plan.objects.annotate(
        user_count=Count('userprofile')
    ).order_by('-user_count').first()
    popular_plan_name = popular_plan.plan_name if popular_plan else 'N/A'
    
    # Calculate payment success rate
    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(paid=True).count()
    success_rate = round((successful_payments / total_payments * 100) if total_payments > 0 else 0, 1)
    
    # Prepare data for user growth chart
    user_growth_data = []
    user_growth_labels = []
    for i in range(6):
        month = datetime.now().month - i
        year = datetime.now().year
        if month < 1:
            month += 12
            year -= 1
        count = Userprofile.objects.filter(start_date__month=month, start_date__year=year).count()
        user_growth_data.insert(0, count)
        user_growth_labels.insert(0, f"{month}/{year}")
    
    # Prepare data for revenue chart
    revenue_data = []
    revenue_labels = []
    for i in range(6):
        month = datetime.now().month - i
        year = datetime.now().year
        if month < 1:
            month += 12
            year -= 1
        revenue = sum(plan.cost * plan.userprofile_set.filter(
            is_active=True, start_date__month=month, start_date__year=year).count() 
            for plan in Plan.objects.all())
        revenue_data.insert(0, revenue)
        revenue_labels.insert(0, f"{month}/{year}")
    
    # Prepare data for plan distribution chart
    plan_data = []
    plan_labels = []
    for plan in Plan.objects.all():
        plan_data.append(plan.userprofile_set.filter(is_active=True).count())
        plan_labels.append(plan.plan_name)
    
    # Prepare data for payment status chart
    payment_status_data = [successful_payments, total_payments - successful_payments]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_plans': total_plans,
        'popular_plan': popular_plan_name,
        'success_rate': success_rate,
        'user_growth_data': user_growth_data,
        'user_growth_labels': user_growth_labels,
        'revenue_data': revenue_data,
        'revenue_labels': revenue_labels,
        'plan_data': plan_data,
        'plan_labels': plan_labels,
        'payment_status_data': payment_status_data,
    }
    
    return render(request, 'analytics.html', context)