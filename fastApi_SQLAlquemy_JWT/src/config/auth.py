from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.config import settings
from config.deps import get_session
from config.security import verificar_senha
from models.usuario import UsuarioModel

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


async def autenticar(
    email: str, senha: str, db: AsyncSession
) -> Optional[UsuarioModel]:
    async with db:
        query = select(UsuarioModel).filter(UsuarioModel.email == email)
        result = await db.execute(query)
        usuario: UsuarioModel = result.unique().scalars().one_or_none()

        if not usuario:
            return None
        if not verificar_senha(senha, usuario.senha):
            return None
        return usuario


def criar_token(tipo_token: str, tempo_vida: timedelta, sub: str) -> str:
    payload = {}
    sp = timezone("America/Sao_Paulo")
    expira = datetime.now(tz=sp) + tempo_vida

    payload["type"] = tipo_token
    payload["exp"] = expira
    payload["iat"] = datetime.now(tz=sp)
    payload["sub"] = str(sub)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def criar_token_acesso(sub: str) -> str:
    return criar_token(
        tipo_token="access_token",
        tempo_vida=timedelta(minutes=settings.ACESS_TOKEN_EXPIRE_MINUTES),
        sub=sub,
    )


async def get_current_user(
    db: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_schema),
) -> UsuarioModel:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        username: str = payload.get("sub")

        if username is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    async with db:
        query = select(UsuarioModel).filter(UsuarioModel.email == username)
        print("user", username)
        result = await db.execute(query)
        usuario: UsuarioModel = result.unique().scalars().one_or_none()
        print("userario", usuario.nome)
        if usuario:
            return usuario
        else:
            raise credential_exception
