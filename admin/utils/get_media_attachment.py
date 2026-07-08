from maxapi.enums import UploadType
from maxapi.types import AttachmentUpload, PhotoAttachmentPayload
from maxapi.types.attachments.attachment import AttachmentPayload


async def get_media_attachment(token: str):
    return AttachmentUpload(
        type=UploadType.IMAGE,
        payload=PhotoAttachmentPayload(token=token)
    )