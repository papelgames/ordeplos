import logging
import os

from flask import render_template, redirect, url_for, request, current_app, abort
from flask.helpers import flash
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import Personas, TiposGestiones, Permisos, Roles, Tareas
from . import abms_bp
from .forms import AltaPersonasForm, TiposForm, PermisosForm, RolesForm, TareasForm, TareasPorTipoDeGestionForm, PermisosSelectForm

#from app.common.mail import send_email
from time import strftime, gmtime


logger = logging.getLogger(__name__)

#creo una tupla para usar en el campo select del form que quiera que necesite los tipo de gestiones
def permisos_select():
    permisos = Permisos.get_all()
    select_permisos =[( '','Seleccionar permiso')]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite las tareas
def tareas_correlativas_select():
    tareas = Tareas.get_all()
    select_tareas =[(0,'Seleccionar Tarea')]
    for rs in tareas:
        sub_select_tareas = (rs.id, rs.descripcion)
        select_tareas.append(sub_select_tareas)
    return select_tareas

#creo una tupla para usar en el campo select del form que quiera que necesite las tareas
def tareas_select(id_tipo_gestion):
    tareas = Tareas.get_tareas_no_relacionadas_tipo_gestion(id_tipo_gestion)
    select_tareas =[(0,'Seleccionar Tarea')]
    for rs in tareas:
        sub_select_tareas = (rs.id, rs.descripcion)
        select_tareas.append(sub_select_tareas)
    return select_tareas

@abms_bp.route("/abms/altapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_persona():
    form = AltaPersonasForm()                                                                                                                   

    if form.validate_on_submit():
        descripcion_nombre = form.descripcion_nombre.data
        correo_electronico = form.correo_electronico.data
        telefono = form.telefono.data
        cuit = form.cuit.data
        tipo_persona = form.tipo_persona.data 
        nota = form.nota.data
        persona_por_cuit = Personas.get_by_cuit(cuit)
        if persona_por_cuit:
            flash ("Ya existe la persona","alert-warning")
            return redirect(url_for('public.index'))

        persona = Personas(descripcion_nombre= descripcion_nombre,
                           correo_electronico = correo_electronico,
                           telefono = telefono,
                           cuit = cuit,
                           tipo_persona = tipo_persona,
                           nota = nota,
                           usuario_alta = current_user.username)
        persona.save()
        flash("Se ha creado la persona correctamente.", "alert-success")
        return redirect(url_for('gestiones.gestiones'))
    return render_template("abms/alta_datos_persona.html", form = form)


@abms_bp.route("/abms/actualizacionpersona/<int:id_persona>", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def actualizacion_persona(id_persona):
    form=AltaPersonasForm()
    persona = Personas.get_by_id(id_persona)
    if form.validate_on_submit():
        form.populate_obj(persona)
        persona.usuario_modificacion = current_user.username
        
        persona.save()
        flash("Se ha actualizado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    
    for campo in list(request.form.items())[1:]:
        data_campo = getattr(form,campo[0]).data
        setattr(persona,campo[0], data_campo)

    return render_template("abms/modificacion_datos_persona.html", form=form, persona = persona)

@abms_bp.route("/abms/altatipogestiones/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_tipo_gestion():
    form = TiposForm()
    tipos = TiposGestiones.get_all()
    if form.validate_on_submit():
        descripcion = form.tipo.data

        tipo_gestion = TiposGestiones(descripcion=descripcion)

        tipo_gestion.save()
        flash("Nuevo tipo de gestión creada", "alert-success")
        return redirect(url_for('abms.alta_tipo_gestion'))

    return render_template("abms/alta_tipo_gestion.html", form=form, tipos=tipos)

# @abms_bp.route("/abms/altatipobienes/", methods = ['GET', 'POST'])
# @login_required
# @admin_required
# @not_initial_status
# def alta_tipo_bien():
#     form = TiposForm()
#     tipos = TiposBienes.get_all()
#     if form.validate_on_submit():
#         descripcion = form.tipo.data

#         tipo_bien = TiposBienes(descripcion=descripcion)

#         tipo_bien.save()
#         flash("Nuevo tipo de bien creado", "alert-success")
#         return redirect(url_for('abms.alta_tipo_bien'))

#     return render_template("abms/alta_tipo_bien.html", form=form, tipos=tipos)

@abms_bp.route("/abms/altapermisos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_permiso():
    form = PermisosForm()
    permisos = Permisos.get_all()
    if form.validate_on_submit():
        descripcion = form.permiso.data

        permiso = Permisos(descripcion=descripcion)

        permiso.save()
        flash("Nuevo permiso creado", "alert-success")
        return redirect(url_for('abms.alta_permiso'))

    return render_template("abms/alta_permisos.html", form=form, permisos=permisos)

@abms_bp.route("/abms/crearroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def crear_roles():
    form = RolesForm()
    
    todos_los_roles = Roles.get_all()

    if form.validate_on_submit():
        rol = Roles(descripcion = form.descripcion.data.upper(),
                    usuario_alta = current_user.username
        )
        rol.save() 
        
        flash ('Rol creado correctamente', 'alert-success')
        return redirect(url_for('abms.crear_roles'))
    return render_template("abms/alta_roles.html", form=form, todos_los_roles=todos_los_roles)

@abms_bp.route("/abms/asignarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    permisos_en_rol = Roles.get_by_id(id_rol)
    
    form = PermisosSelectForm()
    form.id_permiso.choices=permisos_select()
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_rol in permisos_en_rol.permisos:
            if permiso_en_rol.id == int(form.id_permiso.data):
                flash ('El rol ya tiene el permiso', 'alert-warning')
                return redirect(url_for('abms.asignar_permisos_roles', id_rol = id_rol))    
        
        permisos_en_rol.permisos.append(permiso)
        permisos_en_rol.save()
        print ("llego")
        flash ('Permiso asignado correctamente del rol', 'alert-success')
        return redirect(url_for('abms.asignar_permisos_roles', id_rol = id_rol))
    return render_template("abms/alta_permisos_en_roles.html", form=form, permisos_en_rol=permisos_en_rol)

@abms_bp.route("/abms/eliminarpermisosroles/<id_rol>", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permisos_roles(id_rol):
    rol = Roles.get_all_by_id(id_rol)
    rol.delete()    
    flash ('Permiso eliminado correctamente del rol', 'alert-success')
    return redirect(url_for('abms.crear_roles', rol = rol.descripcion))

@abms_bp.route("/abms/altatareas/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_tarea():
    form = TareasForm()
    form.correlativa_de.choices=tareas_correlativas_select()

    if form.validate_on_submit():
        descripcion = form.descripcion.data
        correlativa_de = form.correlativa_de.data
        dias_para_vencimiento = form.dias_para_vencimiento.data
        fecha_unica = form.fecha_unica.data
        carga_dibujante = form.carga_dibujante.data
        
        tarea = Tareas(descripcion=descripcion, 
                           correlativa_de=correlativa_de,
                           dias_para_vencimiento=dias_para_vencimiento,
                           fecha_unica=fecha_unica,
                           carga_dibujante=carga_dibujante,
                           activo= True,
                           usuario_alta=current_user.username)

        #tarea.tipos_gestiones.append(tipos)

        tarea.save()
        flash("Nuevo tarea creado", "alert-success")
        return redirect(url_for('abms.alta_tarea'))
    #falta paginar tareas
    tareas = Tareas.get_all()    
    return render_template("abms/alta_tarea.html", form=form, tareas=tareas)

@abms_bp.route("/abms/modificatarea/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def modificar_tarea():
    id_tarea = request.args.get('id_tarea','')
    
    tarea = Tareas.get_first_by_id(id_tarea)
        
    form = TareasForm(obj=tarea)
    form.correlativa_de.choices=tareas_correlativas_select()

    if form.validate_on_submit():
        form.populate_obj(tarea)
        tarea.usuario_modificacion = current_user.username
        print (form.fecha_unica.data)
        print (form.carga_dibujante.data)
        print (form.activo.data)
        
        tarea.save()
        flash("La tarea ha sido actualizada", "alert-success")
        return redirect(url_for('abms.alta_tarea'))
    
    for campo in list(request.form.items())[1:]:
        data_campo = getattr(form,campo[0]).data
        setattr(tarea,campo[0], data_campo)
  
    return render_template("abms/modificacion_tarea.html", form=form, tarea=tarea)


@abms_bp.route("/abms/eliminartarea/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_tarea():
    id_tarea = request.args.get('id_tarea','')
    tarea = Tareas.get_first_by_id(id_tarea)
    if tarea.gestiones_de_tareas:
        tarea.activo = False
        tarea.save()
    else:
        tarea.delete()    
        flash ('Tarea eliminada correctamente del rol', 'alert-success')
    return redirect(url_for('abms.alta_tarea'))

@abms_bp.route("/abms/altatareasportipodegestion/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_tareas_por_tipo_gestion():
    id_tipo_gestion = request.args.get('id_tipo_gestion','')

    form = TareasPorTipoDeGestionForm()
    form.id_tarea.choices=tareas_select(id_tipo_gestion)
    tipos_gestiones_por_id = TiposGestiones.get_first_by_id(id_tipo_gestion)

    if form.validate_on_submit():
        id_tarea = form.id_tarea.data
        tareas_por_id = Tareas.get_first_by_id(id_tarea)
        tareas_por_id.tipos_gestiones.append(tipos_gestiones_por_id)
        tareas_por_id.save()
   
        flash("Tarea vinculada", "alert-success")
        return redirect(url_for('abms.alta_tareas_por_tipo_gestion', id_tipo_gestion = id_tipo_gestion))
    
    tareas_por_tipo_gestion=TiposGestiones.get_all_by_id(id_tipo_gestion) 
    return render_template("abms/alta_tareas_default.html", form=form,tareas_por_tipo_gestion=tareas_por_tipo_gestion)

@abms_bp.route("/abms/eliminartareaportipogestion/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_tarea_por_tipo_gestion():
    id_tarea = request.args.get('id_tarea','')
    id_tipo_gestion = request.args.get('id_tipo_gestion','')
    tarea = Tareas.get_first_by_id(id_tarea)
    tipo_gestion = TiposGestiones.get_first_by_id(id_tipo_gestion)
    tipo_gestion.tareas.remove(tarea)
    tipo_gestion.save()
 
       
    flash ('Tarea eliminada correctamente del tipo de gestion', 'alert-success')
    return redirect(url_for('abms.alta_tareas_por_tipo_gestion', id_tipo_gestion = id_tipo_gestion))