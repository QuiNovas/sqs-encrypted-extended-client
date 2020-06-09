from json import dumps as jsondumps
from sqs_extended_client.session import SQSExtendedClientSession, RESERVED_ATTRIBUTE_NAME, MESSAGE_POINTER_CLASS
from uuid import uuid4


def _delete_default_kms_key_id(self):
  if hasattr(self, '__default_kms_key_id'):
    del self.__default_kms_key_id


def _get_default_kms_key_id(self):
  return getattr(self, '__default_kms_key_id', None)


def _set_default_kms_key_id(self, kms_key_id):
  assert isinstance(kms_key_id, str) or not kms_key_id
  setattr(self, '__default_kms_key_id', kms_key_id)


def _delete_kms_key_ids(self):
  if hasattr(self, '__kms_key_ids'):
    setattr(self, '__kms_key_ids', {})


def _get_kms_key_ids(self):
  if not hasattr(self, '__kms_key_ids'):
    setattr(self, '__kms_key_ids', {})
  return getattr(self, '__kms_key_ids')

def _set_kms_key_ids(self, kms_key_ids):
  assert isinstance(kms_key_ids, dict) or not kms_key_ids
  setattr(self, '__kms_key_ids', kms_key_ids or {})


def _add_kms_key_id(self, queue_url, kms_key_id):
  assert isinstance(queue_url, str)
  assert isinstance(kms_key_id, str) or not kms_key_id
  if kms_key_id:
    self.kms_key_ids['queue_url'] = kms_key_id
  else :
    self.del_kms_key_id(queue_url)


def _del_kms_key_id(self, queue_url):
  assert isinstance(queue_url, str)
  if queue_url in self.kms_key_ids:
    del self.kms_key_ids[queue_url]


def _get_kms_key_id(self, queue_url):
  return self.kms_key_ids.get(queue_url, None)


def _store_in_s3_encrypted(self, queue_url, message_attributes, message_body):
  encoded_body = message_body.encode()
  if self.large_payload_support and (self.always_through_s3 or self._is_large_message(message_attributes, encoded_body)):
    message_attributes[RESERVED_ATTRIBUTE_NAME] = {}
    message_attributes[RESERVED_ATTRIBUTE_NAME]['DataType'] = 'Number'
    message_attributes[RESERVED_ATTRIBUTE_NAME]['StringValue'] = str(len(encoded_body))
    s3_key = str(uuid4())
    put_args = {
      'ACL': 'private',
      'Body': encoded_body,
      'ContentLength': len(encoded_body)
    }
    kms_key_id = self.get_kms_key_id(queue_url) or self.default_kms_key_id
    if kms_key_id:
        put_args['ServerSideEncryption'] = 'aws:kms'
        put_args['SSEKMSKeyId'] = kms_key_id
    self.s3.Object(self.large_payload_support, s3_key).put(**put_args)
    message_body = jsondumps({MESSAGE_POINTER_CLASS: {'s3BucketName': self.large_payload_support, 's3Key': s3_key}}, separators=(',', ':'))
  return message_attributes, message_body


def _add_custom_attributes(class_attributes):
  class_attributes['default_kms_key_id'] = property(
    _get_default_kms_key_id, 
    _set_default_kms_key_id, 
    _delete_default_kms_key_id
  )
  class_attributes['kms_key_ids'] = property(
    _get_kms_key_ids, 
    _set_kms_key_ids, 
    _delete_kms_key_ids
  )
  class_attributes['add_kms_key_id'] = _add_kms_key_id
  class_attributes['del_kms_key_id'] = _del_kms_key_id
  class_attributes['get_kms_key_id'] = _get_kms_key_id


def _add_client_custom_attributes(base_classes, **kwargs):
  _add_custom_attributes(kwargs['class_attributes'])


def _add_queue_resource_custom_attributes(class_attributes, **kwargs):
  _add_custom_attributes(class_attributes)  


class SQSEncryptedExtendedClientSession(SQSExtendedClientSession):


  def __init__(self, aws_access_key_id=None, aws_secret_access_key=None,
                 aws_session_token=None, region_name=None,
                 botocore_session=None, profile_name=None):
    super().__init__(
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      aws_session_token=aws_session_token,
      region_name=region_name,
      botocore_session=botocore_session,
      profile_name=profile_name
    )
    self.events.register('creating-client-class.sqs', _add_client_custom_attributes)
    self.events.register('creating-resource-class.sqs.Queue', _add_queue_resource_custom_attributes)
