# third party imports
from celery import shared_task


# local imports
from account.tasks import send_email
from job_seeker.models import Application
from employer.models import JobOpportunity

@shared_task(default_retry_count=30 , max_retries=5)
def send_resume_status(apply_pk , log_pk) :

    
    try :
        apply = Application.objects.get(pk=apply_pk)
        employer = apply.job_opportunity.employer.user.email
    except Exception as e:
        return f"error occured while getting the job applications : {e}"
    
    if apply.status == "seen" :
        status = "رزومه شما توسط کارفرما دیده شد"
    elif apply.status == "interview" :
        status = "وضعیت رزومه شما توسط کارفرما به دعوت مصاحبه تغییر پیدا کرد"
    elif apply.status == "accepted" :
        status = "وضعیت رزومه شما توسط کارفرما به تایید شده تغییر پیدا کرد"
         
    job_offer = apply.job_opportunity.title
    content = f"""
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تغییر وضعیت رزومه</title>
        <style>
            /* فونت وزیر */
            @import url('https://fonts.googleapis.com/css2?family=Vazir&display=swap');
            
            body {{
                font-family: 'Vazir', sans-serif;
                direction: rtl;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .email-header h1 {{
                color: #0073e6;
                font-size: 24px;
            }}
            .email-body {{
                font-size: 16px;
                line-height: 1.5;
                color: #333;
            }}
            .email-footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 14px;
                color: #777;
            }}
            .button {{
                background-color: #0073e6;
                color: #fff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                display: inline-block;
            }}
            .button:hover {{
                background-color: #005bb5;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>تغییر وضعیت رزومه شما</h1>
            </div>
            <div class="email-body">
                <p>سلام کارجو عزیز </p>
                <p> وضعیت جدید رزومه شما به شرح زیر است:</p>
                <p><strong>وضعیت جدید: {status}</strong></p>
                <p>برای کسب اطلاعات بیشتر و بررسی وضعیت رزومه خود، لطفاً بر روی دکمه زیر کلیک کنید:</p>
                <a href="http://yourcompany.com/applications/{apply_pk}" class="button">مشاهده وضعیت</a>
            </div>
            <div class="email-footer">
                <p>با تشکر،</p>
                <p>تیم پشتیبانی</p>
                <p>شرکت {job_offer}</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email.apply_async(args=["تغییر وضعیت رزومه" , content , employer , log_pk])
    

@shared_task(default_retry_count=30 , max_retries=5)
def expire_job_offer(job_offer_pk , log_pk) :
    
    try :
        job_offer = JobOpportunity.objects.select_related("employer__user").get(pk=job_offer_pk)
        employer = job_offer.employer.user.email
        job_offer.active = False
        job_offer.save()
    except JobOpportunity.DoesNotExist :
        return "offer does not exists"
    except Exception as e :
        return f"error while expiring the offer : {e}"
    # sending email of expiration
    content = f"""
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>هشدار منقضی شدن موقعیت شغلی</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Vazir&display=swap');
            body {{
                font-family: 'Vazir', sans-serif;
                direction: rtl;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .email-header h1 {{
                color: #e74c3c;
                font-size: 24px;
            }}
            .email-body {{
                font-size: 16px;
                line-height: 1.5;
                color: #333;
            }}
            .email-footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 14px;
                color: #777;
            }}
            .button {{
                background-color: #e74c3c;
                color: #fff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                display: inline-block;
            }}
            .button:hover {{
                background-color: #c0392b;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>هشدار: موقعیت شغلی شما در آستانه منقضی شدن است</h1>
            </div>
            <div class="email-body">
                <p>سلام کارفرما عزیز،</p>
                <p>موقعیت شغلی {job_offer.title} منقضی شد</p>
            </div>
            <div class="email-footer">
                <p>با تشکر،</p>
                <p>تیم پشتیبانی</p>
                <p>شرکت شما</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email("هشدارانقضای موقعیت شغلی" , content , employer , log_pk)
    return "offer expired"

@shared_task(default_retry_count=30 , max_retries=5)
def expire_job_offer_warning(job_offer_pk , log_pk) :
    
    try :
        job_offer = JobOpportunity.objects.get(pk=job_offer_pk)
        employer = job_offer.employer.user.email
    except JobOpportunity.DoesNotExist :
        return "offer does not exists"
    except Exception as e :
        return f"error while expiring the offer : {e}"
    # sending email of expiration
    content = f"""
    <!DOCTYPE html>
    <html lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>هشدار منقضی شدن موقعیت شغلی</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Vazir&display=swap');
            body {{
                font-family: 'Vazir', sans-serif;
                direction: rtl;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .email-header h1 {{
                color: #e74c3c;
                font-size: 24px;
            }}
            .email-body {{
                font-size: 16px;
                line-height: 1.5;
                color: #333;
            }}
            .email-footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 14px;
                color: #777;
            }}
            .button {{
                background-color: #e74c3c;
                color: #fff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                display: inline-block;
            }}
            .button:hover {{
                background-color: #c0392b;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>هشدار: موقعیت شغلی شما در آستانه منقضی شدن است</h1>
            </div>
            <div class="email-body">
                <p>سلام کارفرما عزیز،</p>
                <p>این ایمیل به شما اطلاع می‌دهد که موقعیت شغلی شما در آستانه منقضی شدن است.</p>
                <p>موقعیت شغلی {job_offer.title} , {job_offer.description} در تاریخ {job_offer.expire_at} منقضی خواهد شد</p>
                <a href="http://yourcompany.com/extend_job_offer/{job_offer_pk}" class="button">تمدید موقعیت شغلی</a>
            </div>
            <div class="email-footer">
                <p>با تشکر،</p>
                <p>تیم پشتیبانی</p>
                <p>شرکت شما</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email("هشدارانقضای موقعیت شغلی" , content , employer , log_pk)
    return "offer expired"

