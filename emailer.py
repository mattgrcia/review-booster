import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class Emailer:
    def __init__(
        self,
        to_addresses,
        from_address=os.environ.get("GMAIL_ADDRESS"),
        password=os.environ.get("GMAIL_APP_PASSWORD"),
    ):

        self.to_address = to_addresses
        self.from_address = from_address
        self.password = password

    @staticmethod
    def create_email(subject, body):

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        return msg

    @staticmethod
    def attach_file(msg, filename):

        attachment = open("shipstation_delivered.csv", "rb")
        p = MIMEBase("application", "octet-stream")
        p.set_payload(attachment.read())
        encoders.encode_base64(p)
        p.add_header("Content-Disposition", "attachment; filename= %s" % filename)
        msg.attach(p)

        return msg

    def login(self):

        # creates SMTP session
        session = smtplib.SMTP("smtp.gmail.com", 587)

        # start TLS for security
        session.starttls()

        # Authentication
        session.login(self.from_address, self.password)

        return session

    def send_email(self, subject, body, filename):

        msg = self.create_email(subject, body)
        msg = self.attach_file(msg, filename)

        msg["From"] = self.from_address
        msg["To"] = self.to_address

        session = self.login()

        # sending the mail
        text = msg.as_string()
        session.sendmail(self.from_address, self.to_address, text)

        # terminating the session
        session.quit()

        return None
