#!/usr/bin/env python3

import sys
import pathlib

import random
import time

import smtplib
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.headerregistry import Address
import mimetypes
import ssl

from getpass import getpass


def get_attachments(attachments):
    a = []
    for attachment in attachments:
        ctype, encoding = mimetypes.guess_type(attachment)

        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        with open(attachment, "rb") as f:
            a.append(
                {
                    "content": f.read(),
                    "maintype": maintype,
                    "subtype": subtype,
                    "filename": attachment,
                }
            )
    return a


def make_mail(sender, recipient, subject, body, attachments):
    msg = MIMEMultipart()

    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    for attachment in attachments:
        c = attachment.get("content")
        part = MIMEBase(attachment["maintype"], attachment["subtype"])
        part.set_payload(c)
        part.add_header(
            "Content-Disposition", f"attachment; filename={attachment['filename']}"
        )
        encoders.encode_base64(part)
        msg.attach(part)

    return msg


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send bulk mail.")
    parser.add_argument(
        "recipient_file",
        metavar="RECIPIENTFILE",
        type=pathlib.Path,
        help="File containing the names and emails of recipients.",
    )
    parser.add_argument(
        "body_file",
        metavar="BODYFILE",
        type=pathlib.Path,
        help="Textfile containing mail body.",
    )
    parser.add_argument("--sender", "-f", help="From of the mail")
    parser.add_argument("--subject", "-s", help="Subject of the mail")
    parser.add_argument(
        "--attachment", "-a", nargs="*", default=[], help="Path to Attachment"
    )
    parser.add_argument("--mailhost", "-m", help="Mail host to use for sending.")
    parser.add_argument(
        "--port", "-p", help="Port to use when connecting to mailhost.", type=int
    )
    parser.add_argument(
        "--username", "-u", help="username for connecting to the mail server"
    )
    parser.add_argument("--wait", "-w", type=int, default=10, help="Base for wait")
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Be a bit more verbose"
    )

    args = parser.parse_args()

    body = args.body_file.read_text()
    recipients = args.recipient_file.read_text()

    sender = args.sender or input("From: ")
    subject = args.subject or input("Subject: ")

    attachments = get_attachments(args.attachment)

    mails = [
        make_mail(sender, recipient, subject, body, attachments)
        for recipient in recipients.splitlines()
    ]

    if args.debug:
        print(mails[0])
        if input("Abort? [y/N] ").lower() == "y":
            sys.exit(0)

    username = args.username or input("Username: ")
    password = getpass("Password: ")

    context = ssl.SSLContext()
    with smtplib.SMTP(
        host=args.mailhost or input("Mailhost: "),
        port=args.port or int(input("Port (try 587 if you don't know better): ")),
    ) as s:

        s.ehlo_or_helo_if_needed()
        s.set_debuglevel(args.debug)
        s.starttls(context=context)
        s.ehlo()
        s.login(user=username, password=password)

        for msg in mails:
            print(f"Sending mail to {msg['To']}.", end=" ")
            s.send_message(msg)
            if args.wait > 0:
                wait = args.wait + random.randint(1, 10)
                print(f"Sleeping for {wait} seconds.")
                time.sleep(wait)
