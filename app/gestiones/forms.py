
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
    titular = StringField('Titular', validators=[DataRequired('Debe cargar el nombre o la razón social' )])
    ubicacion_gestion= StringField('Ubicación',validators=[Length(max=50)])
    coordenadas= StringField('Coordenadas',validators=[Length(max=50)])
    id_tipo_bienes = SelectField('Tipo de bien', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de bien')])
    fecha_inicio_gestion = DateField('Fecha de inicio de gestión', validators=[Optional('Debe cargar la fecha de inicio de gestión')])
    fecha_probable_medicion = DateField('Fecha probable de medición', validators=[DataRequired('Debe cargar una fecha probable de medición')])
    id_tipo_gestion = SelectField('Tipo de gestión', choices =[], coerce = str, default = None, validators=[DataRequired('Seleccione tipo de gestión')])
    numero_partido= StringField("Partido",validators=[Length(max=4)])
    numero_partida= StringField("Partida",validators=[Length(max=8)])
    nomenclatura = StringField('Nomenclatura',validators=[Length(max=50)])
    observacion = TextAreaField('Observación', validators=[Length(max=256)])

    def validate_id_dibujante(self, id_dibujante ):
        #valido el formato de la lista de carga
        if len(id_dibujante.data.split('|',)) != 3:
            raise ValidationError('El dibujante cargado no es valido.')
        #dibujante_x_id = Personas.get_by_id(id_dibujante.data.split('|',)[0])
        dibujante_x_id = Users.get_dibujante_persona(id_dibujante.data.split('|',)[0])
        #valido que las personas existan en la tabla de personas. 
        if not dibujante_x_id:
            raise ValidationError('El dibujante seleccionado no es valido.')

    def validate_cuit (self, cuit):
        persona_x_cuit = Personas.get_by_cuit(cuit.data)
        if persona_x_cuit:
            raise ValidationError('El titular que está intentado crear ya existe debe seleccionarlo')

class ModificacionGestionesForm(AltaGestionesForm):
    fecha_medicion = DateField('Fecha de medicion')

class CobrosForm(FlaskForm):
    importe_total = FloatField('Importe total')
    moneda = SelectField('Moneda', choices =[( '','Seleccionar acción'),( "peso",'Pesos'),( "dolar",'Dolar')], coerce = str, default = None, validators=[DataRequired('Seleccione moneda de cobro')])
    #estado = db.Column(db.Integer)
    observacion = TextAreaField('Observación', validators=[Length(max=256)])

class ImportesCobrosForm(FlaskForm):
    fecha_cobro = DateField('Fecha de cobro', validators=[DataRequired('Debe cargar la fecha de cobro' )])
    importe = FloatField('Importe cobrado', validators=[DataRequired('Debe cargar el importe cobrado' )])
    tipo_cambio = FloatField('Tipo de cambio')
    moneda = SelectField('Moneda', choices =[( '','Seleccionar acción'),( "peso",'Pesos'),( "dolar",'Dolar')], coerce = str, default = None, validators=[DataRequired('Seleccione moneda de cobro')])
    medio_cobro = SelectField('Medio de cobro', choices =[( '','Seleccionar acción'), ( 'Cheque','Cheque'),( 'Transferencia','Transferencia'),( 'Efectivo','Efectivo')], coerce = str, default = None, validators=[DataRequired('Seleccione un medio de cobro')])
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