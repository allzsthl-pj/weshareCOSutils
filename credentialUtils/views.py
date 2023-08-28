import json
from django.shortcuts import HttpResponse
from django.conf import settings
import boto3
from loguru import logger
import base64

s3 = boto3.resource('s3')
s3_client = boto3.client('s3',
                         region_name=settings.REGION,
                         config=boto3.session.Config(s3={'addressing_style': 'virtual'},
                                                     signature_version='s3v4'))


# 打印所有存储桶中的文件信息
def print_out_bucket_names(request):
    bucket_names = {}
    index = 0
    for bucket in s3.buckets.all():
        bucket_index = "bucket" + str(index)
        bucket_names[bucket_index] = bucket.name
        index = index + 1
        print(bucket.name)
    return HttpResponse(json.dumps(bucket_names), content_type='application/json')


# 获取图片列表
# header: noteid
# eg: .../?noteid=1
def get_images_list(request):
    logger.info(f'Start getting images from s3.')
    try:
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='image/note' + request.GET.get('noteid') + '/')
    except Exception as e:
        logger.error(f'Get image list failed. | Exception: {e}')
        return HttpResponse("error")

    image_name_list = []
    for obj in all_obj:
        image_path = obj.key
        image_name_list.append(image_path)
    return HttpResponse(json.dumps(image_name_list), content_type='application/json')


# 获取图片链接（用于预览和下载）
# header: noteid
# eg: .../?noteid=1
def get_images_url(request):
    logger.info(f'Start getting image URLs from s3.')
    try:
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='image/note' + request.GET.get('noteid') + '/')
    except Exception as e:
        logger.error(f'Get image URLs failed. | Exception: {e}')
        return HttpResponse("Get image URLS failed")

    image_url_list = []
    for obj in all_obj:
        image_url = "https://" + settings.BUCKET_NAME + ".s3" + "." + \
                    settings.REGION + ".amazonaws.com/" + obj.key
        image_url_list.append(image_url)
    return HttpResponse(json.dumps(image_url_list), content_type='application/json')


# 获取文件列表
# header: noteid
# eg: .../?noteid=1
def get_files_list(request):
    logger.info(f'Start getting files from s3.')
    try:
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='file/note' + request.GET.get('noteid') + '/')
    except Exception as e:
        logger.error(f'Get image list failed. | Exception: {e}')
        return HttpResponse("error")

    file_name_list = []
    for obj in all_obj:
        file_path = obj.key
        file_name_list.append(file_path)
    return HttpResponse(json.dumps(file_name_list), content_type='application/json')


# 获取文件链接（用于下载）
# header: noteid
# eg: .../?noteid=1
def get_files_url(request):
    logger.info(f'Start getting file URLs from s3.')
    try:
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='file/note' + request.GET.get('noteid') + '/')
    except Exception as e:
        logger.error(f'Get file URLs failed. | Exception: {e}')
        return HttpResponse("Get file URLS failed")

    file_url_list = []
    for obj in all_obj:
        file_url = "https://" + settings.BUCKET_NAME + ".s3" + "." + \
                   settings.REGION + ".amazonaws.com/" + obj.key
        file_url_list.append(file_url)
    return HttpResponse(json.dumps(file_url_list), content_type='application/json')


# 删除指定key的图片
# 返回删除，对应note的图片列表
# header: key, noteid
# eg: .../?key=image/note1/Grimer.png&noteid=1
def delete_image(request):
    key_exist = 'key' in request.GET
    noteid_exist = 'noteid' in request.GET
    if key_exist & noteid_exist:
        image_key = request.GET.get('key')
        s3.Object(settings.BUCKET_NAME, image_key).delete()
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='image/note' + request.GET.get('noteid'))
        image_name_list = []
        for obj in all_obj:
            image_path = obj.key
            image_name_list.append(image_path)
        return HttpResponse(json.dumps(image_name_list), content_type='application/json')
    else:
        return HttpResponse('invalid parameters')


# 删除指定key的文件（excel）
# 返回删除，对应note的文件列表
# header: key, noteid
# eg: .../?key=file/note1/test.xlsx&noteid=1
def delete_file(request):
    key_exist = 'key' in request.GET
    noteid_exist = 'noteid' in request.GET
    if key_exist & noteid_exist:
        file_key = request.GET.get('key')
        s3.Object(settings.BUCKET_NAME, file_key).delete()
        bucket = s3.Bucket(settings.BUCKET_NAME)
        all_obj = bucket.objects.filter(Prefix='file/note' + request.GET.get('noteid'))
        file_name_list = []
        for obj in all_obj:
            file_path = obj.key
            file_name_list.append(file_path)
        return HttpResponse(json.dumps(file_name_list), content_type='application/json')
    else:
        return HttpResponse('invalid parameters')


# 上传图片到指定note目录下
# body: dir, name, imgData
# dir: 对应note的noteid，例如'dir': 1将图片上传到存储桶image/note1/目录下
# name: 图片名(xxx.png)，暂时只支持png，可根据实际需要改写
# imgData: 图片的base64字符串，前端使用js读取图片，转化为base64字符串，通过post请求传到后端
# 后端对接收到的数据进行解码，写入本地temp文件，再进行二进制读取，将读取的数据用过aws接口上传到存储桶中
def upload_image(request):
    if request.method == 'POST':
        body = request.body
        image_data = json.loads(body.decode())['imgData']
        image_name = json.loads(body.decode())['name']
        image_dir = json.loads(body.decode())['dir']
        image_path = "temp.png"
        file = open(image_path, 'wb')
        file.write(base64.b64decode(image_data))
        with open(image_path, 'rb') as f:
            data = f.read()
        response = s3.Bucket(settings.BUCKET_NAME).put_object(
            Key='image/note' + image_dir + '/' + image_name,
            Body=data
        )
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse('invalid parameters')


# 上传文件（excel）到指定目录下
# 其他与上传图片同理
def upload_file(request):
    if request.method == 'POST':
        body = request.body
        file_data = json.loads(body.decode())['fileData']
        file_name = json.loads(body.decode())['name']
        file_dir = json.loads(body.decode())['dir']
        file_path = "temp.xlsx"
        file = open(file_path, 'wb')
        file.write(base64.b64decode(file_data))
        with open(file_path, 'rb') as f:
            data = f.read()
        response = s3.Bucket(settings.BUCKET_NAME).put_object(
            Key='file/note' + file_dir + '/' + file_name,
            Body=data
        )
        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse('invalid parameters')
