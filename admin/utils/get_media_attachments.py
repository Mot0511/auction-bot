from maxapi.enums import UploadType
from maxapi.types import AttachmentUpload, PhotoAttachmentPayload, AttachmentPayload
from db import DBService
from typing import List


async def get_media_attachments(tokens: List[int]):
    attachments = []
    for token in tokens:
        attachments.append(
            AttachmentUpload(
                type=UploadType.IMAGE,
                payload=AttachmentPayload(token=token)
            )
        )

    return attachments