import PhotoService_pb2
import PhotoService_pb2_grpc
from time import localtime, strftime
import grpc

import io
import PIL.Image as Image

def run():
    with grpc.insecure_channel('localhost:9009') as channel:
        request = PhotoService_pb2.PhotoesRequest(uuid="pepe.png")
        stub = PhotoService_pb2_grpc.PhotoServiceStub(channel)
        print(f'{log_time()} Reply received')
        response = stub.requestPhotoes(request)
                
        image = Image.open(io.BytesIO(response.image))
        image.show()
        
def log_time():
    return strftime("[%H:%M:%S %d/%m/%Y]", localtime())

if __name__ == "__main__":
    run()