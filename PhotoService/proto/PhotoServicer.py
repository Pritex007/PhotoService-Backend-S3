import PhotoService_pb2
import PhotoService_pb2_grpc
from concurrent import futures
from time import localtime, strftime
import grpc
import io
import sys
from minio import Minio
from enum import Enum

Debug = False

class Constants():
    class Methods():
        get='GET'
    class Minio():
        endpoint='host.docker.internal:9000' if not Debug else 'localhost:9000'
        bucket_name='photos'
        access_key='minioadmin'
        secret_key='minioadmin'
        secure=False
    class Server():
        insecure_port='0.0.0.0:9009' if not Debug else "localhost:9009"
        
    

class PhotoServicer(PhotoService_pb2_grpc.PhotoServicer):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.configure()      
    
    def requestPhoto(self, request, context):
        print(f'[Request photo] Request received: {request}', end='')
                
        data_object = self.client.get_object(
            bucket_name=Constants.Minio.bucket_name,
            object_name=request.uuid
            )
        print(f'return {data_object.data}')
        return PhotoService_pb2.PhotoResponse(image=data_object.data)
    
    def addPhoto(self, request, context):
        print(f'[Add photo] Request received: {request.uuid}', end='')
        
        url = self.client.get_presigned_url(
            method=Constants.Methods.get,
            bucket_name=Constants.Minio.bucket_name,
            object_name=request.uuid
            )
        
        print(f'URL: {url}')
        
        data_stream = io.BytesIO(request.image)
        self.client.put_object(
            bucket_name=Constants.Minio.bucket_name,
            object_name=request.uuid,
            data=data_stream,
            length=len(data_stream.getvalue())
            )
        return PhotoService_pb2.AddPhotoResponse(status=True, url=url)
    
    def removePhoto(self, request, context):
        print(f'[Remove photo] Request received: {request}', end='')
                  
        self.client.remove_object(
            bucket_name=Constants.Minio.bucket_name, 
            object_name=request.uuid
            )
        return PhotoService_pb2.RemovePhotoResponse(status=True)
    
    def configure(self):
        if len(self.client.list_buckets()) == 0:
            self.client.make_bucket(bucket_name=Constants.Minio.bucket_name)
    

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    photoServicer = PhotoServicer(
        Minio(
            endpoint=Constants.Minio.endpoint,          # адрес сервера
            access_key=Constants.Minio.access_key,      # логин админа
            secret_key=Constants.Minio.secret_key,      # пароль админа
            secure=Constants.Minio.secure               # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение
            )
        )
    PhotoService_pb2_grpc.add_PhotoServicer_to_server(photoServicer, server)
    server.add_insecure_port(Constants.Server.insecure_port)
    server.start()
    server.wait_for_termination() 

if __name__ == "__main__":
    server()