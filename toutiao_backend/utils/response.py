from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

def success_response(message: str="success", data=None):
    content = {
        "code":200,
        "message": message,
        "data": data
    }

    #目标：把任何的FastAPI、pydantic、ORM对象都要正常响应 (用jsonable_encoder)
    return JSONResponse(content=jsonable_encoder(content))

