# snailmail

A script for sending mails.

The only dependency is Python 3.6+ as it only uses the standard library.

To see all possible options:
```
snailmail.py -h
```

It might be a bit rough around the edges, but it has been tested with all the
advertised functionality (sending mails with attachments).

The only non-optional input are two files, one with the mail body and one with a
list of recipients, one per line.

The text of the mail body must (so far) be static and is not templated.

The file with mail addresses is only supposed to contain those, _NO_ pretty
names (e.g. `John Doe <john.doe@example.com>`), so please _ONLY_ mail addresses
(e.g. `john.doe@example.com`)`.
