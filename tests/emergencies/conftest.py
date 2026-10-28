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
def client(db_session):
    #hace que el endpoint use la sesión de prueba y no la BD real
    app.dependency_overrides[get_db] = lambda: db_session 
    #cuando un endopint solicite la dependencia get_db, utiliza db_session en su lugar
    with TestClient(app) as test_client: 
        '''TestClient es una clase que permite enviar 
        solicitudes HTTP de prueba a una aplicación FastAPi'''
        yield test_client #entrega el cliente al test mediante yield
    app.dependency_overrides.clear() #la sustitución se deja de aplicar

'''
Paso a paso cuando pytest ejecuta un test:
1-Prepara la base de datos temporal
2-Configura el reemplazo de get_db
3-Crear test_client
4-Entrega el cliente al test mediante yield
5-El test realiza la solicitud http
6-Al terminar, se reanuda el fixture y se limipia el cliente
'''
