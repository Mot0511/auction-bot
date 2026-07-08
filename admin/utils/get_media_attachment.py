from maxapi.enums import UploadType
from maxapi.types import AttachmentUpload, PhotoAttachmentPayload, AttachmentPayload


async def get_media_attachment(token: str):
    return AttachmentUpload(
        type=UploadType.IMAGE,
        payload=AttachmentPayload(token=token)
    )