from crisisops.modules.emergencies.schemas import EmergencyValidate
from crisisops.modules.emergencies.models import Emergency
from crisisops.modules.emergencies.exceptions import EmergencyValidationError
from pydantic import ValidationError #clase de excepción de Pydantic utiliza cuando falla una validación. Captura errores especificamente de pydantic. 

def schemas_validate_emergency(emergency: Emergency) -> None:

    

    try:
       
       EmergencyValidate.model_validate(emergency) #si la validación de los campos necesarios se cumplen, no se retorna nada solo permite la emergencia para su posterior evaluación

    
    except ValidationError as e: #captura una excepción de tipo ValidationError y lo almancena en la variable e

        errors = {} #diccionario que ocuparmos para retornar en caso que no se cumpla la estructura requeria los campos faltantes

        for error in e.errors():


            field = "-".join(map(str,error["loc"])) #Obtiene la ubicación del campo que produjo el error de validación. Si el error esta en un campo simple como Severity, el resultado es "severity"
            #Si el error esta en un atributo de un objeto, devuelve ("clase_x, "atributo y") -> clase_x-atributo y
            #Si el error está en un elemento de una lista: ("lista_clase",0->indice,atributo de la clase)--->"lista_clase-indice-atributo"

            type_error = error["type"] #tipo de error como, por ejemplo: error por cadena de texto -> string type

            message = error["msg"] #mensaje en ingles que se retorna para mayor comprensión

            errors[field] = {"type":type_error, "message":message}

        #from e indica que la nueva excepción fue causada por ValidationError capturado anteriormente.
        raise  EmergencyValidationError(errors) from e #acá el diccionario con los errores se prograga a travez de la clase  EmergencyValidationError que hereda de DomainError y esta a su vez de Exception.
        #Debe heredar de exception para que permita progagar/subir el error.


