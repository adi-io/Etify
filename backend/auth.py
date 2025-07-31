from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=401, detail="Invalid authentication scheme.")
            decoded_token = self.verify_jwt(credentials.credentials)
            if not decoded_token:
                raise HTTPException(status_code=401, detail="Invalid credentials.")
            return decoded_token
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials.")

    def verify_jwt(self, jwtoken: str):
        try:
            decoded_token = jwt.decode(jwtoken, JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            return decoded_token
        except JWTError:
            return None
