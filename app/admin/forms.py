from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, SelectField, HiddenField, IntegerField, DateField)
from wtforms.validators import DataRequired, Length,Email, NumberRange, Optional
from app.common.controles import validar_correo, validar_cuit, validar_cuit_guardado


class UserAdminForm(FlaskForm):
    is_admin = BooleanField('¿Administrador?')
    es_dibujante = BooleanField('¿Es dibujante?')
    
class PermisosUserForm(FlaskForm):
    id_permiso = SelectField('Permiso', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione un permiso')])

class RolesUserForm(FlaskForm):
    rol = SelectField('Rol', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione un rol')])


class DatosPersonasForm(FlaskForm):
    id = HiddenField('id')
    descripcion_nombre = StringField("Nombre/Razón Social", validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    correo_electronico = StringField('Correo electrónico', validators=[Optional(), Email(), validar_correo])
    telefono = StringField('Telefono')
    cuit = StringField('CUIT', validators=[DataRequired('Debe completar el numero de cuit'), Length(max=11), validar_cuit, validar_cuit_guardado])
    tipo_persona = SelectField('Tipo de persona', choices =[( '','Seleccionar acción'),( "fisica",'Persona Física'),( "juridica",'Persona Jurídica')], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de persona')])
    genero = SelectField('Genero', choices =[( '','Seleccionar genero'),( "M",'Masculino'),( "F",'Femenino'),( "X",'No Binario'),( "E",'Empresa/Persona Jurídica' )], coerce = str, default = None, validators=[DataRequired('Seleccione genero')])
    fecha_nacimiento  = DateField('Fecha cita')
    direccion = StringField('Dirección', validators=[DataRequired('Debe cargar dirección' )])
    id_localidad = StringField('Localidad', validators=[DataRequired('Debe cargar la localidad' )])
    nota = TextAreaField('Nota', validators=[Length(max=256)])

class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar', validators=[DataRequired('Escriba la descripción de un producto o su código de barras' )])

class TiposForm(FlaskForm):
    tipo = StringField('Nuevo tipo', validators=[DataRequired('Escriba una descripción' )])

class PermisosForm(FlaskForm):
    proceso = SubmitField('Procesar permisos')

class TareasForm(FlaskForm):
    descripcion = StringField('Nueva tarea', validators=[DataRequired('Escriba una descripción' )])
    correlativa_de = SelectField('Correlativa de', choices =[], coerce = int)
    dias_para_vencimiento = IntegerField('Dias para el vencimiento')
    fecha_unica = BooleanField('¿es fecha única?')
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

class DocumentosForm(FlaskForm):    
    id_tipo_documento = SelectField('Tipo de documento', choices =[], coerce = int, validators=[NumberRange(min=1, message="Debe ingresar una tipo de documento")])
    descripcion =StringField('Descripcion de documento', validators=[DataRequired('Escriba una descripción' ),Length(max=50)])
    texto = HiddenField('texto')

class VariablesDocumentosForm(FlaskForm):
    nombre_variable = StringField('Nombre de la variable', validators=[DataRequired('Escriba una descripción'),Length(max=100)])
    descripcion_variable = StringField('Descripcion de la variable', validators=[DataRequired('Escriba una descripción'),Length(max=50)])
    
    