import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    """
    Classe de configuração principal do projeto.
    Lê variáveis do ambiente ou do arquivo .env e fornece validação adicional.
    """

    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # Chave secreta usada para JWT
    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # URL de conexão com o banco de dados
    TOKEN_EXPIRE_MINUTES: int = Field(30, env="TOKEN_EXPIRE_MINUTES")  # Expiração do token (em minutos)
    ALGORITHM: str = Field("HS256", env="ALGORITHM")  # Algoritmo usado para assinatura do token

    class Config:
        """
        Configuração interna para o Pydantic Settings.
        Define o arquivo .env e seu encoding.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate(self):
        """
        Valida se as principais variáveis de ambiente foram configuradas corretamente.
        Lança exceção se algum valor essencial estiver ausente ou inseguro.
        """
        if self.SECRET_KEY == "supersecretkeychangeme":
            raise ValueError("A chave secreta não foi configurada corretamente no arquivo .env.")
        if not self.DATABASE_URL:
            raise ValueError("A URL do banco de dados não foi configurada corretamente no arquivo .env.")
        return self

# Instância global das configurações
settings = Settings()

# Validação explícita após carregamento
settings.validate()
