import boto3
import sqs_extended_client

from .session import SQSEncryptedExtendedClientSession, _store_in_s3_encrypted

sqs_extended_client.session._store_in_s3 = _store_in_s3_encrypted

# Monkey patch to use our Session object instead of boto3's
boto3.session.Session = SQSEncryptedExtendedClientSession

# Now take care of the reference in the boto3.__init__ module
setattr(boto3, 'Session', SQSEncryptedExtendedClientSession)

# Now ensure that even the default session is our SQSEncryptedExtendedClientSession
if boto3.DEFAULT_SESSION:
  boto3.setup_default_session()
