import logging
import os

from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, not_initial_status, nocache
from app.auth.models import Users
from app.models import  Permisos, Roles, Tareas, Personas, TiposGestiones, Estados, TiposDocumentos, ModelosDocumentos
from . import admin_bp
from .forms import UserAdminForm, PermisosUserForm, RolesUserForm, TareasForm, DatosPersonasForm, TiposForm, PermisosForm, RolesForm, PermisosSelectForm, EstadosForm, TareasPorTipoDeGestionForm, DocumentosForm

from app.common.funciones import listar_endpoints


logger = logging.getLogger(__name__)

#creo una tupla para usar en el campo select del form que quiera que necesite los permisos
def permisos_select(user_id):
    permisos = Permisos.get_permisos_no_relacionadas_personas(user_id)
    select_permisos =[]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite los permisos
def permisos_en_roles_select(rol_id):
    permisos = Permisos.get_permisos_no_relacionadas_roles(rol_id)
    select_permisos =[]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite los roles
def roles_select():
    roles = Roles.get_all()
    select_rol =[( '','Seleccionar permiso')]
    for rs in roles:
        sub_select_rol = (str(rs.id), rs.descripcion)
        select_rol.append(sub_select_rol)
    return select_rol

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
    select_tareas =[]
    for rs in tareas:
        sub_select_tareas = (rs.id, rs.descripcion)
        select_tareas.append(sub_select_tareas)
    return select_tareas

#creo una tupla para usar en el campo select del form que quiera que necesite los tipos de documento
def tipos_documentos_select():
    tareas = TiposDocumentos.get_all()
    select_tp_documentos =[(0,'Seleccionar tipos de documentos')]
    for rs in tareas:
        sub_select_tp_documentos = (rs.id, rs.descripcion)
        select_tp_documentos.append(sub_select_tp_documentos)
    return select_tp_documentos

@admin_bp.route("/admin/")
@login_required
@admin_required
@not_initial_status
def index():
    return render_template("admin/index.html")

@admin_bp.route("/admin/users/")
@login_required
@admin_required
@not_initial_status
def list_users():
    users = Users.get_all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/admin/user/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def update_user_form():
    user_id = request.args.get('user_id','')
    
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    # Crea un formulario inicializando los campos con
    # los valores del usuario.
    form = UserAdminForm(obj=user)
    if form.validate_on_submit():
        # Actualiza los campos del usuario existente
        # user.is_admin = form.is_admin.data
        # user.es_dibujante = form.es_dibujante.data
        form.populate_obj(user)
        user.save()
        logger.info(f'Guardando el usuario {user_id}')
        return redirect(url_for('admin.list_users'))
    return render_template("admin/user_form.html", form=form, user=user)


@admin_bp.route("/admin/user/delete/", methods=['POST', ])
@login_required
@admin_required
@not_initial_status
def delete_user():
    user_id = request.args.get('user_id','')
    user = Users.get_by_id(user_id)
    logger.info(f'Se va a eliminar al usuario {user_id}')
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    user.delete()
    logger.info(f'El usuario {user_id} ha sido eliminado')
    return redirect(url_for('admin.list_users'))

@admin_bp.route("/admin/asignacionpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_permisos():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = PermisosUserForm()
    form.id_permiso.choices = permisos_select(user_id)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_user in user.permisos:
            if permiso_en_user.id == int(form.id_permiso.data):
                flash ('El usuario ya tiene el permiso', 'alert-warning')
                return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
        user.permisos.append(permiso)
        user.save()
        
        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
    return render_template("admin/permisos_usuarios.html", form=form, user=user)

@admin_bp.route("/admin/asignacionroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_roles():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = RolesUserForm()
    form.rol.choices = roles_select()
    
    if form.validate_on_submit():
        permisos_de_roles = Roles.get_by_id(form.rol.data)
        for permiso in permisos_de_roles.permisos:
            control = True
            for permiso_en_user in user.permisos:
                if permiso_en_user.id == permiso.id:
                    control = False
                
            if control:
                user.permisos.append(permiso)
              
        user.save()

        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_roles', user_id = user_id))
    return render_template("admin/roles_usuarios.html", form=form, user=user)


@admin_bp.route("/admin/eliminarpermisousuario/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso_usuario():
    user_id = request.args.get('user_id','')
    id_permiso = request.args.get('id_permiso','')
    user = Users.get_by_id(user_id)
    permiso = Permisos.get_by_id(id_permiso)
    
    user.permisos.remove(permiso)
    user.save()
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('admin.asignacion_permisos', user_id = user_id))

@admin_bp.route("/admin/altapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_persona():
    form = DatosPersonasForm()                                                                                                                   

    if form.validate_on_submit():
        descripcion_nombre = form.descripcion_nombre.data
        correo_electronico = form.correo_electronico.data
        telefono = form.telefono.data
        cuit = form.cuit.data
        tipo_persona = form.tipo_persona.data 
        nota = form.nota.data

        persona = Personas(descripcion_nombre= descripcion_nombre,
                           correo_electronico = correo_electronico,
                           telefono = telefono,
                           cuit = cuit,
                           tipo_persona = tipo_persona,
                           nota = nota,
                           usuario_alta = current_user.username)
        persona.save()
        flash("Se ha creado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    return render_template("admin/datos_persona.html", form = form)

@admin_bp.route("/admin/actualizacionpersona/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def actualizacion_persona():
    id_persona = request.args.get('id_persona','')
    persona = Personas.get_by_id(id_persona)
    form=DatosPersonasForm(obj=persona)
    if form.validate_on_submit():
        form.populate_obj(persona)
        persona.save()
        flash("Se ha actualizado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    
    for campo in list(request.form.items())[1:]:
        data_campo = getattr(form,campo[0]).data
        setattr(persona,campo[0], data_campo)
    return render_template("admin/datos_persona.html", form=form, persona = persona)

@admin_bp.route("/admin/altatipogestiones/", methods = ['GET', 'POST'])
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
        return redirect(url_for('admin.alta_tipo_gestion'))

    return render_template("admin/alta_tipo_gestion.html", form=form, tipos=tipos)

@admin_bp.route("/admin/altapermisos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_permiso():
    form = PermisosForm()
    permisos = Permisos.get_all()
    if form.validate_on_submit():
        permisos_obj = []
        
        for item in listar_endpoints(current_app):
            check_permiso = Permisos.get_by_descripcion(item.get('descripcion'))
            if not check_permiso:
                permiso = Permisos(**item)
                permisos_obj.append(permiso)
        if permisos_obj:
            q_altas = len(permisos_obj)
            permiso.save_masivo(permisos_obj)
            flash(f"Se han creado {q_altas} permisos", "alert-success")
        else:
            flash(f"No hay nuevos permisos", "alert-warning")
        return redirect(url_for('admin.alta_permiso'))

    return render_template("admin/alta_permisos.html", form=form, permisos=permisos)

@admin_bp.route("/admin/eliminarpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso():
    id_permiso = request.args.get('id_permiso','')
    permiso = Permisos.get_by_id(id_permiso)
    permiso.delete()
    
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('admin.alta_permiso'))

@admin_bp.route("/admin/crearroles/", methods=['GET', 'POST'])
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
        return redirect(url_for('admin.crear_roles'))
    return render_template("admin/alta_roles.html", form=form, todos_los_roles=todos_los_roles)

@admin_bp.route("/admin/asignarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    permisos_en_rol = Roles.get_by_id(id_rol)
    
    form = PermisosSelectForm()
    form.id_permiso.choices=permisos_en_roles_select(id_rol)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_rol in permisos_en_rol.permisos:
            if permiso_en_rol.id == int(form.id_permiso.data):
                flash ('El rol ya tiene el permiso', 'alert-warning')
                return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))    
        
        permisos_en_rol.permisos.append(permiso)
        permisos_en_rol.save()

        flash ('Permiso asignado correctamente del rol', 'alert-success')
        return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))
    return render_template("admin/alta_permisos_en_roles.html", form=form, permisos_en_rol=permisos_en_rol)

@admin_bp.route("/admin/eliminarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    id_permiso = request.args.get('id_permiso','')
    rol = Roles.get_by_id(id_rol)
    permiso = Permisos.get_by_id(id_permiso)
    rol.permisos.remove(permiso)
    rol.save()  
    
    flash ('Permiso eliminado correctamente del rol', 'alert-success')
    return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))

@admin_bp.route("/admin/altatareas/", methods = ['GET', 'POST'])
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
        
        tarea = Tareas(descripcion=descripcion, 
                           correlativa_de=correlativa_de,
                           dias_para_vencimiento=dias_para_vencimiento,
                           fecha_unica=fecha_unica,
                           activo= True,
                           usuario_alta=current_user.username)

        #tarea.tipos_gestiones.append(tipos)

        tarea.save()
        flash("Nuevo tarea creado", "alert-success")
        return redirect(url_for('admin.alta_tarea'))
    #falta paginar tareas
    tareas = Tareas.get_all()    
    return render_template("admin/alta_tarea.html", form=form, tareas=tareas)

@admin_bp.route("/admin/modificatarea/", methods = ['GET', 'POST'])
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
        tarea.save()
        flash("La tarea ha sido actualizada", "alert-success")
        return redirect(url_for('admin.alta_tarea'))
    
    for campo in list(request.form.items())[1:]:
        data_campo = getattr(form,campo[0]).data
        setattr(tarea,campo[0], data_campo)
  
    return render_template("admin/modificacion_tarea.html", form=form, tarea=tarea)


@admin_bp.route("/admin/eliminartarea/", methods=['GET', 'POST'])
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
    return redirect(url_for('admin.alta_tarea'))

@admin_bp.route("/admin/altatareasportipodegestion/", methods = ['GET', 'POST'])
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
        return redirect(url_for('admin.alta_tareas_por_tipo_gestion', id_tipo_gestion = id_tipo_gestion))
    
    tareas_por_tipo_gestion=TiposGestiones.get_all_by_id(id_tipo_gestion) 
    return render_template("admin/alta_tareas_default.html", form=form,tareas_por_tipo_gestion=tareas_por_tipo_gestion)

@admin_bp.route("/admin/eliminartareaportipogestion/", methods=['GET', 'POST'])
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
    return redirect(url_for('admin.alta_tareas_por_tipo_gestion', id_tipo_gestion = id_tipo_gestion))

@admin_bp.route("/admin/altaestados/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_estados():
    form = EstadosForm()
    
    if form.validate_on_submit():
        clave = form.clave.data
        descripcion = form.descripcion.data
        tabla = form.tabla.data
        inicial = form.inicial.data
        final = form.final.data
        
        estado = Estados(clave=clave,
                         descripcion=descripcion,
                         tabla=tabla,
                         inicial=inicial,
                         final=final,
                         usuario_alta=current_user.username)
        
        estado.save()
        flash("Nuevo estado creado", "alert-success")
        return redirect(url_for('admin.alta_estados'))
    #falta paginar tareas
    estados = Estados.get_all()    
    return render_template("admin/alta_estados.html", form=form, estados=estados)

@admin_bp.route("/admin/altatipodocumentos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_tipo_documento():
    form = TiposForm()
    tipos = TiposDocumentos.get_all()
    if form.validate_on_submit():
        descripcion = form.tipo.data

        tipo_gestion = TiposDocumentos(descripcion=descripcion)

        tipo_gestion.save()
        flash("Nuevo tipo de documento creado", "alert-success")
        return redirect(url_for('admin.alta_tipo_documento'))

    return render_template("admin/alta_tipo_documento.html", form=form, tipos=tipos)

@admin_bp.route("/admin/altadocumentos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_documento_modelo():
    form = DocumentosForm()
    form.id_tipo_documento.choices=tipos_documentos_select()
    campos = [column.name for column in TiposDocumentos.__table__.columns]
    if form.validate_on_submit():
       
        id_tipo_documento = 1 #form.id_tipo_documento.data
        descripcion = form.descripcion.data
        contenido_html = form.contenido_html.data
        tipo_documento = TiposDocumentos.get_first_by_id(id_tipo_documento)
        print("DEBUG:", id_tipo_documento, descripcion, contenido_html)
        documento = ModelosDocumentos(descripcion=descripcion,
                                         texto=contenido_html)
        print("DEBUG 2:", tipo_documento.descripcion)
        tipo_documento.modelos_documentos.append(documento)
        tipo_documento.save()
        flash("Nuevo tipo de documento creado", "alert-success")
        return redirect(url_for('admin.alta_documento_modelo'))
    return render_template("admin/documentos_modelos.html", form=form, campos=campos)
   