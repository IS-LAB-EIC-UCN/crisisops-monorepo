import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app


@pytest.fixture() #Esto le indica a pytest, esta función no es un test. 
#Es una función que prepara recursos  que otros Test pueden necesitar
#luego pytest reconoce que existe un fixture con ese nombre db_session() 
#por ejemplo cuando se ocupa en def 
#test_minimal_report_is_persisted_with_empty_optional_fields(client, db_session)
def db_session():
    #Base de datos sqllite solo en memoria: rápida, desechable, no toca postgresql
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", 
        #se utiliza sqlite en memoria para los test porque es rápida, 
        #no necesita levantar un servidor postgresql y permite trabajar con datos temporales
        connect_args={"check_same_thread": False}, 
        #Se permite que una única conexión física  de SQLite 
        #sea transferida o compartida entre hilos de python.
        poolclass=StaticPool, 
        #permite reutilizar una misma conexión de base de datos dentro del engine. 
        #De esta manera, las operaciones del test pueden 
        #trabajar sobre la misma base de datos en memoria
    )

    Base.metadata.create_all(bind=engine) #crea las tablas desde los modelos
    session = sessionmaker(bind=engine)() 
    #se crea una sesión configurada para trabajar con la base de datos temporal de pruebas.
    yield session #el test corre aquí
    session.close()#limpieza al terminar el test
    Base.metadata.drop_all(bind=engine) 

@pytest.fixture()
def anonymous_client(db_session):
    """Cliente SIN cabeceras X-Actor / X-Actor-Role: cada prueba envía las suyas."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session):
    """Cliente que actúa como `coordinador1` con rol COORDINATOR en todas sus peticiones
    (puede registrar, editar y validar). Para probar otro rol usa `headers_for(...)`."""
    app.dependency_overrides[get_db] = lambda: db_session
    headers = {"X-Actor": "coordinador1", "X-Actor-Role": "COORDINATOR"}
    with TestClient(app, headers=headers) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def headers_for():
    """headers_for("OPERATOR") -> cabeceras de un usuario con ese rol."""

    def _headers(role: str, username: str | None = None) -> dict[str, str]:
        return {"X-Actor": username or f"{role.lower()}1", "X-Actor-Role": role}

    return _headers
'''
Paso a paso cuando pytest ejecuta un test:
1-Prepara la base de datos temporal
2-Configura el reemplazo de get_db
3-Crear test_client
4-Entrega el cliente al test mediante yield
5-El test realiza la solicitud http
6-Al terminar, se reanuda el fixture y se limipia el cliente
'''
