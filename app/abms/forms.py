
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, IntegerField, DateField, SelectField)
from wtforms.fields import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange
from app.models import Personas

class AltaPersonasForm(FlaskForm):
    descripcion_nombre = StringField("Nombre/Razón Social", validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    correo_electronico = StringField('Correo electrónico', validators=[Email()])
    telefono = StringField('Telefono')
    cuit = StringField('CUIT', validators=[DataRequired(), Length(max=11)])
    tipo_persona = SelectField('Tipo de persona', choices =[( '','Seleccionar acción'),( "fisica",'Persona Física'),( "juridica",'Persona Jurídica')], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de persona')])
    #estado = SelectField('Tipo de persona', choices =[], coerce = str, default = None)
    nota = TextAreaField('Nota', validators=[Length(max=256)])

        
    def validate_correo_electronico(self, correo_electronico):
        correo_persona = Personas.get_by_correo(correo_electronico.data)
        if correo_persona:
            raise ValidationError('El correo electrónico pertenece a otra persona.')

class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar', validators=[DataRequired('Escriba la descripción de un producto o su código de barras' )])

class TiposForm(FlaskForm):
    tipo = StringField('Nuevo tipo', validators=[DataRequired('Escriba una descripción' )])

class PermisosForm(FlaskForm):
    permiso = StringField('Nuevo permiso', validators=[DataRequired('Escriba una descripción' )])

class TareasForm(FlaskForm):
    descripcion = StringField('Nueva tarea', validators=[DataRequired('Escriba una descripción' )])
    correlativa_de = SelectField('Correlativa de', choices =[], coerce = int)
    dias_para_vencimiento = IntegerField('Dias para el vencimiento')
    fecha_unica = BooleanField('¿es fecha única?')
    carga_dibujante = BooleanField('¿Carga dibujante?')
    activo = BooleanField('¿Activo?')

class RolesForm(FlaskForm):
    descripcion = StringField('Rol',validators=[DataRequired('Debe ingresar un rol'),Length(max=15)])
    
class TareasPorTipoDeGestionForm(FlaskForm):
    id_tarea = SelectField('Tarea', choices =[], coerce = int, validators=[NumberRange(min=1, message="Debe ingresar una tarea")])

class PermisosSelectForm(FlaskForm):
    id_permiso = SelectField('Permiso', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione un permiso')])

class EstadosForm(FlaskForm):
    clave = IntegerField('Clave', validators=[DataRequired('Escriba una clave')])
    descripcion = StringField('Nuevo estado', validators=[DataRequired('Escriba una descripción'),Length(max=50)])
    tabla = StringField('Tabla de referencia', validators=[DataRequired('Escriba una descripción'),Length(max=50)])
    inicial = BooleanField('¿Es inicial?')
    final = BooleanField('¿Es final?')

