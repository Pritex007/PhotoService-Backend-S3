import PhotoService_pb2
import PhotoService_pb2_grpc
from time import localtime, strftime
import grpc

import io
import PIL.Image as Image

def run():
    with grpc.insecure_channel('localhost:9009') as channel:
        photoRequest = PhotoService_pb2.PhotoRequest(uuid="pepe.png")
        stub = PhotoService_pb2_grpc.PhotoStub(channel)
        print(f'{log_time()} Reply received')
        response = stub.requestPhoto(photoRequest)
                
        image = Image.open(io.BytesIO(response.image))
        image.show()
        
        addRequest = PhotoService_pb2.AddPhotoRequest(uuid='skibidi.png', image=response.image)
        add_response = stub.addPhoto(addRequest)
        
        print(f'[Add response]{add_response}')
        
def log_time():
    return strftime("[%H:%M:%S %d/%m/%Y]", localtime())

if __name__ == "__main__":
    run()