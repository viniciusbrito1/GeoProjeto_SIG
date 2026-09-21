from fastapi import HTTPException


class ErroNegocio(HTTPException):
    """Erro de regra de negócio com mensagem em português e ação corretiva (RNF-05)."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
