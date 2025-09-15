# 🚀 Teste Python - FastAPI + SQLAlchemy

Este projeto é uma aplicação backend desenvolvida com **FastAPI**, **SQLAlchemy** e **JWT** para autenticação.  
O objetivo é servir como base para criação de APIs modernas, seguras e escaláveis em Python.

---

## ⚙️ Tecnologias Utilizadas
- [FastAPI](https://fastapi.tiangolo.com/) 🚀
- [SQLAlchemy](https://www.sqlalchemy.org/) 🗄️
- [Pydantic](https://docs.pydantic.dev/) ✅
- [PyJWT](https://pyjwt.readthedocs.io/) 🔐
- [Pytest](https://docs.pytest.org/) 🧪

---

## ▶️ Como Rodar o Projeto
### 1. Clonar o repositório
```bash
git clone https://github.com/ismaelcorrea2025/teste-python.git
cd teste-python

### 1. Clonar o repositório
```bash
git clone https://github.com/ismaelcorrea2025/teste-python.git
cd teste-python

______2-Criar ambiente virtual______

python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

_____3-Instalar dependências____

pip install -r requirements.txt

______4-Rodar a API______

uvicorn main:app --reload

___________________________________________________________________

A API estará disponível em:
👉 http://127.0.0.1:8000

Documentação automática:
	•	Swagger UI: http://127.0.0.1:8000/docs
	•	Redoc: http://127.0.0.1:8000/redoc

como rodar os testes: pytest -v
