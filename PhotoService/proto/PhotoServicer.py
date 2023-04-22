import PhotoService_pb2
import PhotoService_pb2_grpc
from concurrent import futures
from time import localtime, strftime
import grpc
from minio import Minio

class PhotoServicer(PhotoService_pb2_grpc.PhotoServiceServicer):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client          
    
    def requestPhotoes(self, request, context):
        print(f'{log_time()} Request received: {request}')
                
        # выгрузка объекта из хранилища в ваш файл              
        data_object = self.client.get_object(
            bucket_name='photos',  # необходимо указать имя бакета,  
            object_name=request.uuid  # и путь к файлу для записи
            )
        return PhotoService_pb2.PhotoesResponse(image=data_object.data)
    

def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    photoServicer = PhotoServicer(
        Minio(
            endpoint="host.docker.internal:9000",  # адрес сервера
            access_key='minioadmin',    # логин админа
            secret_key='minioadmin',    # пароль админа
            secure=False                # опциональный параметр, отвечающий за вкл/выкл защищенное TLS соединение
            )
        )
    PhotoService_pb2_grpc.add_PhotoServiceServicer_to_server(photoServicer, server)
    server.add_insecure_port("0.0.0.0:9009")
    server.start()
    server.wait_for_termination()
    
def log_time():
    return strftime("[%H:%M:%S %d/%m/%Y]", localtime())

if __name__ == "__main__":
    server()