import logging
from email.message import EmailMessage
import aiosmtplib
from app.config import settings

logger = logging.getLogger(__name__)

async def send_refund_decision_email(customer_email: str, customer_name: str, decision: str, rationale: str):
    """
    Send an email notification to the customer regarding their refund decision.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or settings.SMTP_USER == 'your_mailtrap_user':
        logger.warning(f"SMTP not configured. Skipping email to {customer_email}")
        logger.info(f"Mock Email -> To: {customer_email} | Result: {decision} | Rationale: {rationale}")
        return

    subject = f"Update on your Refund Request: {decision.capitalize()}"
    
    # HTML formatted email
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #1a73e8;">Refund Request Update</h2>
        <p>Hi <strong>{customer_name}</strong>,</p>
        <p>We wanted to provide you an update regarding your recent refund request. After careful review, the status of your request is currently: <strong>{decision.upper()}</strong>.</p>
        
        <div style="background-color: #f8faff; border-left: 4px solid #1a73e8; padding: 15px; margin: 20px 0;">
            <p style="margin: 0;">{rationale}</p>
        </div>
        
        <p>If you have any questions, you can reply directly to this email or visit our support portal.</p>
        <p>Thank you,<br/><strong>The Refund AI Team</strong></p>
      </body>
    </html>
    """

    message = EmailMessage()
    message["From"] = settings.FROM_EMAIL
    message["To"] = customer_email
    message["Subject"] = subject
    message.set_content(f"Hi {customer_name},\n\nYour refund request is: {decision.upper()}.\n\nReason: {rationale}\n\nThanks,\nRefund AI")
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False,
            start_tls=True if settings.SMTP_PORT == 587 else False
        )
        logger.info(f"Successfully sent refund decision email to {customer_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {customer_email}: {e}")
