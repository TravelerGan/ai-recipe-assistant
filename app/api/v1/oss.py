import alibabacloud_oss_v2 as oss
from fastapi import APIRouter, HTTPException
from datetime import timedelta
import os
# 加载环境变量
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# OSS 域名配置
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.getenv("OSS_BUCKET")


@router.get("/oss/presign")
def presign_upload(filename: str):
    if not OSS_BUCKET:
        raise HTTPException(status_code=503, detail="OSS_BUCKET is not configured")
    try:
        credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    except oss.exceptions.CredentialsEmptyError as exc:
        raise HTTPException(status_code=503, detail="OSS credentials are not configured") from exc

    config = oss.config.load_default()
    config.credentials_provider = credentials_provider
    config.region = os.getenv("OSS_REGION", "cn-beijing")
    client = oss.Client(config)

    # 根据文件扩展名判断 Content-Type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    content_type = content_type_map.get(ext, "application/octet-stream")

    pre_result = client.presign(oss.PutObjectRequest(
        bucket=OSS_BUCKET,
        key=filename,
        content_type=content_type,
    ), expires=timedelta(seconds=3600))

    # 返回上传 URL 和可访问的图片路径
    return {
        "uploadUrl": pre_result.url.strip('"'),
        "contentType": content_type,
        "accessUrl": f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{filename}"
    }
