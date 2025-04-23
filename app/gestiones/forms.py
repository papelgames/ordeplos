from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField, DecimalField)
from wtforms.fields import FloatField, IntegerField 
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, Optional
from app.models import Personas
from app.auth.models import Users
from app.common.controles import validar_correo, validar_cuit_guardado, validar_cuit, required_conditional_cuit,required_conditional_dni


class BusquedaForm(FlaskForm):
    buscar = StringField('Buscar')

class AltaGestionesForm(FlaskForm):
    origen = StringField('Origen', validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    fecha_inicio_gestion = DateField('Fecha de inicio de gestión', validators=[Optional('Debe cargar la fecha de inicio de gestión')])
    id_tipo_gestion = SelectField('Tipo de gestión', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de gestión')])
    fecha_cita  = DateField('Fecha cita')
    cita = BooleanField('¿Hubo cita?')
    observacion = TextAreaField('Observación', validators=[Length(max=256)])
    
    
class AltaGestionesPersonasForm(AltaGestionesForm):
    id = HiddenField('id')
    descripcion_nombre = StringField("Nombre/Razón Social", validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    genero = SelectField('Genero', choices =[( '','Seleccionar genero'),( "M",'Masculino'),( "F",'Femenino'),( "X",'No Binario'),( "E",'Empresa/Persona Jurídica' )], coerce = str, default = None, validators=[DataRequired('Seleccione genero')])
    tipo_persona = SelectField('Tipo de persona', choices =[( '','Seleccionar tipo de persona'),( "fisica",'Persona Física'),( "juridica",'Persona Jurídica')], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de persona')])
    correo_electronico = StringField('Correo electrónico', validators=[Email(), validar_correo])
    telefono = StringField('Telefono') 
    dni = StringField('DNI', validators=[required_conditional_dni, Length(max=8)])
    cuit = StringField('CUIT', validators=[required_conditional_cuit, Length(max=11), validar_cuit_guardado, validar_cuit])

class ModificacionGestionesForm(AltaGestionesForm):
    fecha_medicion = DateField('Fecha de medicion')

class CobrosForm(FlaskForm):
    importe_total = FloatField('Importe total')
    moneda = SelectField('Moneda', choices =[( '','Seleccionar moneda'),( "peso",'Pesos'),( "dolar",'Dolar')], coerce = str, default = None, validators=[DataRequired('Seleccione moneda de cobro')])
    #estado = db.Column(db.Integer)
    observacion = TextAreaField('Observación', validators=[Length(max=256)])

class ImportesCobrosForm(FlaskForm):
    fecha_cobro = DateField('Fecha de cobro', validators=[DataRequired('Debe cargar la fecha de cobro' )])
    importe = FloatField('Importe cobrado', validators=[DataRequired('Debe cargar el importe cobrado' )])
    tipo_cambio = FloatField('Tipo de cambio')
    moneda = SelectField('Moneda', choices =[( '','Seleccionar acción'),( "peso",'Pesos'),( "dolar",'Dolar')], coerce = str, default = None, validators=[DataRequired('Seleccione moneda de cobro')])
    medio_cobro = SelectField('Medio de cobro', choices =[( '','Seleccionar medio de cobro'), ( 'Cheque','Cheque'),( 'Transferencia','Transferencia'),( 'Efectivo','Efectivo')], coerce = str, default = None, validators=[DataRequired('Seleccione un medio de cobro')])
    observacion = TextAreaField('Observación', validators=[Length(max=256)])

class PasoForm(FlaskForm):
    observacion = TextAreaField('Observación', validators=[Length(max=256)])

class GestionesTareasForm(FlaskForm):
    id_tarea = SelectField('Nueva tarea', choices =[], coerce = int, validators=[NumberRange(min=1, message="Debe ingresar una tarea")])

class DetallesGdTForm(FlaskForm):
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired('Debe cargar la fecha de inicio de la tarea' )])
    fecha_fin = DateField('Fecha de fin', validators=[Optional()])
    observacion = TextAreaField('Observación', validators=[Length(max=256)])
