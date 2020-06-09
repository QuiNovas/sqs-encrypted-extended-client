# sqs-encrypted-extended-client

### Extends [sqs-extended-client](https://github.com/QuiNovas/sqs-extended-client) adding per queue KMS encryption for S3 objects

## Installation
```
pip install sqs-encrypted-extended-client
```

## Overview
sqs-encrypted-extended-client allows for Server-Side KMS encryption of S3 objects created by 
[sqs-extended-client](https://github.com/QuiNovas/sqs-extended-client) on a global or per-queue basis.

# Usage
All usage for [sqs-extended-client](https://github.com/QuiNovas/sqs-extended-client), with the additional
following use-cases.

### Enabling default KMS key encryption for all queues or for unmatched queues
```python
import boto3
import sqs_extended_client

sqs = boto3.client('sqs')
sqs.large_payload_support = 'my-bucket-name'
sqs.default_kms_key_id = 'alias/my-key'
```
Arguments:
* large_payload_support -- the S3 bucket name that will store large messages.
* default_kms_key_id -- the KMS Key Id to use when there are no matching queues. Can be a key alias (recommended), key id, or key arn.

### Enabling support for a particular queue
```python
import boto3
import sqs_extended_client

sqs = boto3.client('sqs')
sqs.large_payload_support = 'my-bucket-name'
sqs.add_kms_key_id('https://my-queue-url', 'alias/my-key')
```

### Enabling support for a number of queues at once
```python
import boto3
import sqs_extended_client

sqs = boto3.client('sqs')
sqs.large_payload_support = 'my-bucket-name'
sqs.kms_key_ids = {
  'https://my-queue-1-url': 'alias/my-key-1',
  'https://my-queue-2-url': 'alias/my-key-2',
  ...
}
```

