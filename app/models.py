
import datetime
from email.policy import default
from itertools import product
from types import ClassMethodDescriptorType
from typing import Text

#from slugify import slugify
from sqlalchemy import func, or_, alias, not_
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
#from app.auth.models import Users

from app import db

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(),\
                     onupdate=db.func.current_timestamp())

class Personas (Base):
    __tablename__ = "personas"
    descripcion_nombre = db.Column(db.String(50), nullable = False)
    cuit = db.Column(db.String(11), nullable = False)
    dni = db.Column(db.String(8), nullable = False)
    correo_electronico = db.Column(db.String(256))
    telefono = db.Column(db.String(256))
    genero = db.Column(db.String(9))
    fecha_nacimiento = db.Column(db.DateTime)
    tipo_persona = db.Column(db.String(50))
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id'))
    direccion = db.Column(db.String(256))
    id_localidad = db.Column(db.Integer, db.ForeignKey('localidades.id'))
    nota = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))
    titular_gestion = db.relationship('Gestiones', backref='personas', uselist=True, lazy=True)
    personas_en_gestiones = db.relationship('Gestiones', secondary='personasengestiones', back_populates='gestiones_en_personas')

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.flush()
        db.session.commit()

    @staticmethod
    def get_all():
        return Personas.query.all()
    
    @staticmethod
    def get_by_id(id_persona):
        return Personas.query.filter_by(id = id_persona).first()
    
    @staticmethod
    def get_by_cuit(cuit):
        return Personas.query.filter_by(cuit = cuit).first()

    @staticmethod
    def get_by_correo(correo):
        return Personas.query.filter_by(correo_electronico = correo).first()
        
    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = f"%{descripcion_}%"
        return db.session.query(Personas)\
            .filter(Personas.descripcion_nombre.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)

class PersonasEnGestiones (Base):
    __tablename__ = "personasengestiones"
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id')) 
    id_gestion = db.Column(db.Integer, db.ForeignKey('gestiones.id'))
    
class Gestiones (Base):
    __tablename__ = "gestiones"
    id_persona = db.Column(db.Integer, db.ForeignKey('personas.id')) #cliente persona principal
    origen = db.Column(db.String(80), nullable = False)
    edad_en_gestion = db.Column(db.Integer)
    fecha_inicio_gestion = db.Column(db.DateTime)
    fecha_probable_inicio_tramite = db.Column(db.DateTime)
    fecha_fin_gestion = db.Column(db.DateTime)
    cita = db.Column(db.Boolean)
    fecha_cita = db.Column(db.DateTime)
    id_analista_responsable = db.Column(db.Integer)
    id_tipo_gestion = db.Column(db.Integer, db.ForeignKey('tiposgestiones.id'))
    id_estado = db.Column(db.Integer)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    observaciones = db.relationship('Observaciones', backref='gestiones', uselist=True, lazy=True)
    gestiones_de_tareas = db.relationship('GestionesDeTareas', backref='gestiones', uselist=True, lazy=True)
    gestiones_en_personas = db.relationship('Personas', secondary='personasengestiones', back_populates='personas_en_gestiones')
    documentos = db.relationship('Documentos', backref='gestiones', uselist=True)
    cobro = db.relationship('Cobros', backref='cobros', uselist=False)
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_paginated(page=1, per_page=20):
        return Gestiones.query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(id):
        return Gestiones.query.get(id)

    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = f"%{descripcion_}%"
        return Gestiones.query.join(
        Personas, (Gestiones.id_persona == Personas.id)
        ).filter(or_(Personas.descripcion_nombre.ilike(descripcion_),)
        ).paginate(page=page, per_page=per_page, error_out=False)    

    @staticmethod
    def get_gestiones_by_id_cliente_all_paginated(id_persona, page=1, per_page=20):
        return Gestiones.query.filter_by(id_persona = id_persona)\
            .paginate(page=page, per_page=per_page, error_out=False)

class Cobros (Base):
    __tablename__ = "cobros"
    id_gestion = db.Column(db.Integer, db.ForeignKey('gestiones.id'))
    importe_total = db.Column(db.Numeric(precision=15, scale=2))
    importe_cobrado = db.Column(db.Numeric(precision=15, scale=2))
    moneda = db.Column(db.String(25))
    estado = db.Column(db.Integer)
    limitada = db.Column(db.Boolean)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    observaciones = db.relationship('Observaciones', backref='cobros', uselist=True)
    importes_cobros = db.relationship('ImportesCobros', backref='cobro', uselist=True)
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Cobros.query.all()
    
    @staticmethod
    def get_all_by_id_gestion(id_gestion):
        return Cobros.query.filter_by(id_gestion = id_gestion).first()
    
    @staticmethod
    def get_all_by_id_cobro(id_cobro):
        return Cobros.query.filter_by(id = id_cobro).first()

    @staticmethod
    def get_by_id(id_persona):
        return Cobros.query.filter_by(id = id_persona).first()
    
    #reportes
    @staticmethod
    def get_deuda_x_clientes():
        query = db.session.query(
                Personas.descripcion_nombre.label('cliente'),
                (func.sum(Cobros.importe_total) - func.sum(Cobros.importe_cobrado)).label('deuda')
            ).join(Gestiones, Gestiones.id_cliente == Personas.id)\
            .join(Cobros, Cobros.id_gestion == Gestiones.id)
            
        result = query.group_by(
                Personas.descripcion_nombre
            ).all()
        
        return result 

class ImportesCobros (Base):
    __tablename__ = "importescobros"
    id_cobro = db.Column(db.Integer, db.ForeignKey('cobros.id'))
    fecha_cobro = db.Column(db.DateTime, nullable = False)
    importe = db.Column(db.Numeric(precision=15, scale=2))
    tipo_cambio = db.Column(db.Numeric(precision=15, scale=2))
    moneda = db.Column(db.String(25))
    medio_cobro = db.Column(db.String(25))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    observaciones = db.relationship('Observaciones', backref='importe_cobro', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_by_id_cobro(id_cobro):
        return ImportesCobros.query.filter_by(id = id_cobro).first()



class Observaciones (Base):
    __tablename__ = "observaciones"
    id_gestion = db.Column(db.Integer, db.ForeignKey('gestiones.id'))
    id_cobro = db.Column(db.Integer, db.ForeignKey('cobros.id'))
    id_importe_cobro = db.Column(db.Integer, db.ForeignKey('importescobros.id'))
    id_gestion_de_tarea = db.Column(db.Integer, db.ForeignKey('gestionesdetareas.id'))
    observacion = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all_by_id_gestion(id_gestion):
        return Observaciones.query.filter_by(id_gestion = id_gestion).all()

    @staticmethod
    def get_all_by_id_gestion_de_tarea(id_gestion_de_tarea):
        return Observaciones.query.filter_by(id_gestion_de_tarea = id_gestion_de_tarea).all()

class Estados(Base):
    __tablename__ = "estados"
    clave = db.Column(db.Integer)
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    inicial = db.Column(db.Boolean)
    final = db.Column(db.Boolean)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    persona = db.relationship('Personas', backref='estado_personas', uselist=True)
    user = db.relationship('Users', backref='estado_users', uselist=True)
   
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Estados.query.all()
    
    @staticmethod
    def get_first_by_clave_tabla(clave, tabla):
        return Estados.query.filter_by(clave = clave, tabla = tabla).first()


class TiposGestiones(Base):
    __tablename__ = "tiposgestiones"
    descripcion = db.Column(db.String(50))
    limitada = db.Column(db.Boolean)
    tareas = db.relationship('Tareas', secondary='tiposgestionesportareas', back_populates='tipos_gestiones')
    gestiones = db.relationship('Gestiones', backref='tipos_gestiones', uselist=False)

    @staticmethod
    def get_all():
        return TiposGestiones.query.all()

    @staticmethod
    def get_all_by_id(id_tipo_gestion):
        return TiposGestiones.query.filter_by(id = id_tipo_gestion).all()
    
    @staticmethod
    def get_first_by_id(id_tipo_gestion):
        return TiposGestiones.query.filter_by(id = id_tipo_gestion).first()

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

class PermisosPorUsuarios(Base):
    __tablename__ = "permisosporusuarios"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))

class Roles(Base):
    __tablename__ = "roles"
    descripcion = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    permisos = db.relationship('Permisos', secondary='permisosenroles', back_populates='roles')

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_id(id):
        return Roles.query.get(id)

    @staticmethod
    def get_all_by_id(id):
        return Roles.query.filter_by(id = id).all()
    
    @staticmethod
    def get_all():
        return Roles.query.all()

    @staticmethod
    def get_all_descripcion_agrupada():
        return db.session.query(Roles.descripcion.label('nombre_rol')).distinct().all()

class PermisosEnRoles(Base):
    __tablename__ = "permisosenroles"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_roles =db.Column(db.Integer, db.ForeignKey('roles.id'))

class Permisos(Base):
    __tablename__ = "permisos"
    descripcion = db.Column(db.String(50))
    roles = db.relationship('Roles', secondary='permisosenroles', back_populates='permisos')
    users = db.relationship('Users', secondary='permisosporusuarios', back_populates='permisos')
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def save_masivo(self, lista):
        db.session.bulk_save_objects(lista)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Permisos.query.all()

    @staticmethod
    def get_by_id(id_permiso):
        return Permisos.query.filter_by(id = id_permiso).first()

    @staticmethod
    def get_by_descripcion(descripcion):
        return Permisos.query.filter_by(descripcion = descripcion).first()

    @staticmethod
    def get_permisos_no_relacionadas_roles(id_rol): 
        return  Permisos.query.filter(~Permisos.roles.any(id = id_rol)).all()
    
    @staticmethod
    def get_permisos_no_relacionadas_personas(id_persona): 
        return  Permisos.query.filter(~Permisos.users.any(id = id_persona)).all()
  
class GestionesDeTareas(Base):
    __tablename__ = "gestionesdetareas"
    id_gestion = db.Column(db.Integer, db.ForeignKey('gestiones.id'))
    id_tarea = db.Column(db.Integer, db.ForeignKey('tareas.id'))
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    fecha_vencimiento = db.Column(db.DateTime)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    observaciones = db.relationship('Observaciones', backref='gestionesdetareas', uselist=True, lazy=True)
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_gestiones_tareas_pendientes_all_paginated(page=1, per_page=20):
        return GestionesDeTareas.query.filter_by(fecha_fin = None)\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_gestiones_tareas_pendientes__por_gestiones_all_paginated(id_gestion, page=1, per_page=20):
        return GestionesDeTareas.query.filter_by(id_gestion = id_gestion, fecha_fin = None)\
            .paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_by_id_gestion(id_gestion):
        return GestionesDeTareas.query.filter_by(id_gestion = id_gestion).all()
    
    @staticmethod
    def get_all_by_id_gestion_de_tarea(id_gestion_de_tarea):
        return GestionesDeTareas.query.filter_by(id = id_gestion_de_tarea).first()

class Tareas(Base):
    __tablename__ = "tareas"
    descripcion = db.Column(db.String(50))
    correlativa_de = db.Column(db.Integer)
    dias_para_vencimiento = db.Column(db.Integer)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    fecha_unica = db.Column(db.Boolean)
    activo = db.Column(db.Boolean)
    tipos_gestiones = db.relationship('TiposGestiones', secondary='tiposgestionesportareas', back_populates='tareas')
    gestiones_de_tareas = db.relationship('GestionesDeTareas', backref='tareas', uselist=False, lazy=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Tareas.query.all()
    
    @staticmethod
    def get_first_by_id(id_tarea):
        return Tareas.query.filter_by(id = id_tarea).first()

    @staticmethod
    def get_tareas_no_relacionadas(id_gestion): 
        return  Tareas.query.filter(~Tareas.gestiones_de_tareas.has(id_gestion = id_gestion),Tareas.activo == True).all()
    
    @staticmethod
    def get_tareas_no_relacionadas_tipo_gestion(id_tipo_gestion): 
        return  Tareas.query.filter(~Tareas.tipos_gestiones.any(id = id_tipo_gestion),Tareas.activo == True ).all()
    
    
class TiposGestionesPorTareas(Base):
    __tablename__ = "tiposgestionesportareas"
    id_tipo_gestion = db.Column(db.Integer, db.ForeignKey('tiposgestiones.id'))
    id_tarea = db.Column(db.Integer, db.ForeignKey('tareas.id'))

class Documentos(Base):
    __tablename__ = "documentos"
    id_tipo_documento = db.Column(db.Integer, db.ForeignKey('tiposdocumentos.id'))
    id_gestion = db.Column(db.Integer, db.ForeignKey('gestiones.id'))
    texto = db.Column(db.Text(16383))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

class ModelosDocumentos(Base):
    __tablename__ = "modelosdocumentos"
    id_tipo_documento = db.Column(db.Integer, db.ForeignKey('tiposdocumentos.id'))
    descripcion = db.Column(db.String(256))
    texto = db.Column(db.Text(16383))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    @staticmethod
    def get_all():
        return ModelosDocumentos.query.all()
   
    @staticmethod
    def get_first_by_id(id_documento):
        return ModelosDocumentos.query.filter_by(id = id_documento).first()

    @staticmethod
    def get_all_paginated(page=1, per_page=20):
        return ModelosDocumentos.query.paginate(page=page, per_page=per_page, error_out=False)

class TiposDocumentos(Base):
    __tablename__ = "tiposdocumentos"
    descripcion = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    documentos = db.relationship('Documentos', backref='tipos_documentos_d', uselist=True)
    modelos_documentos = db.relationship('ModelosDocumentos', backref='tipos_documentos_md', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return TiposDocumentos.query.all()

    @staticmethod
    def get_first_by_id(id_tipo_documento):
        return TiposDocumentos.query.filter_by(id = id_tipo_documento).first()

class VariablesDocumentos (Base):
    __tablename__ = "variablesdocumentos"
    nombre_variable = db.Column(db.String(100))
    descripcion_variable = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return VariablesDocumentos.query.all()
    
    @staticmethod
    def get_first_by_id(id_variable):
        return VariablesDocumentos.query.filter_by(id = id_variable).first()
    
    @staticmethod
    def get_variables():
        resultados = db.session.query(VariablesDocumentos.nombre_variable).all()
        return [r[0] for r in resultados]

class Localidades (Base):
    __tablename__ = "localidades"
    localidad = db.Column(db.String(256))
    provincia = db.Column(db.String(256))
    personas = db.relationship('Personas', backref='localidades', uselist=True)

    @staticmethod
    def get_by_id(id):
        return Localidades.query.get(id)
    
    @staticmethod
    def get_all():
        return Localidades.query.all()
    
    @staticmethod
    def get_provinvia_like_descripcion(descripcion):
        descripcion = f"%{descripcion}%"
        return db.session.query(Localidades).filter(Localidades.provincia.contains(descripcion)).first()
    
    @staticmethod
    def get_localidad_like_descripcion(descripcion):
        descripcion = f"%{descripcion}%"
        return db.session.query(Localidades).filter(Localidades.localidad.contains(descripcion)).first()