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


def _create_s3_put_object_params_decorater(func):
  def create_put_object_params(*args, **kwargs):
    put_object_params = func(*args, **kwargs)
    kms_key_id = args[0].get_kms_key_id(args[2]) or args[0].default_kms_key_id
    if kms_key_id:
        put_object_params['ServerSideEncryption'] = 'aws:kms'
        put_object_params['SSEKMSKeyId'] = kms_key_id
    return put_object_params
  return create_put_object_params


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
    self.register_client_decorator('sqs', '_create_s3_put_object_params', _create_s3_put_object_params_decorater)
    self.register_resource_decorator('sqs', 'Queue', '_create_s3_put_object_params', _create_s3_put_object_params_decorater)
