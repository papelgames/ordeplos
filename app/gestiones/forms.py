
#from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField, DecimalField)
from wtforms.fields import FloatField, IntegerField 
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, Optional
from app.models import Personas
from app.auth.models import Users

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
    descripcion_nombre = StringField("Nombre/Razón Social", validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    genero = SelectField('Genero', choices =[( '','Seleccionar genero'),( "M",'Masculino'),( "F",'Femenino')], coerce = str, default = None, validators=[DataRequired('Seleccione genero')])
    tipo_persona = SelectField('Tipo de persona', choices =[( '','Seleccionar tipo de persona'),( "fisica",'Persona Física'),( "juridica",'Persona Jurídica')], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de persona')])
    correo_electronico = StringField('Correo electrónico', validators=[Email()])
    telefono = StringField('Telefono')
    dni = StringField('DNI', validators=[DataRequired(), Length(max=8)])
    cuit = StringField('CUIT', validators=[DataRequired(), Length(max=11)])
    #estado = SelectField('Tipo de persona', choices =[], coerce = str, default = None)
    #nota = TextAreaField('Nota', validators=[Length(max=256)])

    def validate_cuit (self, cuit):
        persona_x_cuit = Personas.get_by_cuit(cuit.data)
        if persona_x_cuit:
            raise ValidationError('El titular que está intentado crear ya existe debe seleccionarlo')


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

class DetallesGdTDibujanteForm(DetallesGdTForm):
    id_dibujante = StringField('Dibujante', validators=[DataRequired('Debe elegir un dibujante de la lista' )])