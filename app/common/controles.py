from flask import current_app
from app.models import Personas
from wtforms.validators import DataRequired, Length, Email, ValidationError
from app.common.funciones import generar_cuil_cuit

def validar_correo(self, field ):
    correo_persona = Personas.get_by_correo(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)
    if datos_persona_actual:
        if correo_persona and field.data == correo_persona.correo_electronico and datos_persona_actual and datos_persona_actual.id != correo_persona.id:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')
    else:
        if correo_persona:
            raise ValidationError('El correo electrónico ya está dado de alta en otra persona.')

def validar_cuit_guardado(self, field ):
    cuit_persona = Personas.get_by_cuit(field.data)
    datos_persona_actual = Personas.get_by_id(self.id.data)

    if datos_persona_actual:
        if cuit_persona and field.data == cuit_persona.cuit and datos_persona_actual and datos_persona_actual.id != cuit_persona.id:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')
    else:
        if cuit_persona:
            raise ValidationError('El CUIT ya está dado de alta en otra persona.')
        
def required_conditional_dni(self, field ):
    if not self.cuit.data and not field.data:
        raise ValidationError(f'Debe completar el DNI o el CUIT ')

def required_conditional_cuit(self, field ):
    if not self.dni.data and not field.data:
        raise ValidationError(f'Debe completar el DNI o el CUIT ')   
 
def validar_cuit(self, field ):
    if field.data:
        cuit_valido =generar_cuil_cuit(field.data[2:10], self.genero.data)
        if field.data != cuit_valido:
            raise ValidationError(f'El cuit no es valido. CUIT correcto: {cuit_valido}')   
