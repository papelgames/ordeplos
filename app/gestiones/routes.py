import logging

import os
from time import ctime
from datetime import date, datetime, timedelta

from flask import render_template, redirect, url_for, current_app, flash, send_file, request #, make_response, abort
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, not_initial_status, nocache
from app.auth.models import Users
from app.models import Personas, TiposGestiones, Gestiones, Observaciones, Cobros, ImportesCobros, Tareas, GestionesDeTareas, PersonasEnGestiones, ModelosDocumentos, Documentos, VariablesDocumentos, Localidades
from . import gestiones_bp 
from .forms import AltaGestionesForm,AltaGestionesPersonasForm, BusquedaForm, CobrosForm, ImportesCobrosForm, PasoForm, GestionesTareasForm, DetallesGdTForm, DocumentosForm

from app.common.mail import send_email
from app.common.funciones import generar_cuil_cuit, renderizar_modelo_con_instancia

logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

#creo una tupla para usar en el campo select del form que quiera que necesite los tipo de gestiones
def tipo_gestion_select():
    tipos_gestiones = TiposGestiones.get_all()
    select_tipo_gestion =[( '','Seleccionar tipo de gestión')]
    for rs in tipos_gestiones:
        sub_select_tipo_gestion = (str(rs.id), rs.descripcion)
        select_tipo_gestion.append(sub_select_tipo_gestion)
    return select_tipo_gestion

#creo una tupla para usar en el campo select del form que quiera que necesite las tareas
def tareas_select(id_gestion):
    tareas = Tareas.get_tareas_no_relacionadas(id_gestion)
    select_tareas =[(0,'Seleccionar Tarea')]
    for rs in tareas:
        sub_select_tareas = (rs.id, rs.descripcion)
        select_tareas.append(sub_select_tareas)
    return select_tareas

#creo una tupla para usar en el campo select del form que quiera que necesite las tareas
def modelos_documentos_select():
    modelos_documentos = ModelosDocumentos.get_all()
    select_modelos_documentos =[(0,'Seleccionar modelo de documento')]
    for rs in modelos_documentos:
        sub_select_modelos_documentos = (rs.id, rs.descripcion)
        select_modelos_documentos.append(sub_select_modelos_documentos)
    return select_modelos_documentos

@gestiones_bp.route("/gestiones/altagestiones/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_gestiones():
    id_cliente = request.args.get('id_cliente','')
    origen_gestion = Personas.get_all()
    localidades = Localidades.get_all()
    persona = Personas.get_by_id(id_cliente)
    form = AltaGestionesPersonasForm(obj=persona)                                                                                                                   
    form.id_tipo_gestion.choices = tipo_gestion_select()
    if request.method == "GET":
        # Solo setea fecha si no tiene nada (primera carga)
        if not form.fecha_cita.data:
            form.fecha_cita.data = date.today()
        if not form.fecha_inicio_gestion.data:
            form.fecha_inicio_gestion.data = date.today()

    if not id_cliente:
        con_persona = False
        if form.validate_on_submit():
            descripcion_nombre = form.descripcion_nombre.data
            genero = form.genero.data
            tipo_persona = form.tipo_persona.data
            correo_electronico = form.correo_electronico.data
            telefono = form.telefono.data
            dni = form.dni.data
            cuit = form.cuit.data
            direccion = form.direccion.data
            localidad = form.localidad.data.split('|')
            origen = form.origen.data
            fecha_inicio_gestion = form.fecha_inicio_gestion.data
            id_tipo_gestion = form.id_tipo_gestion.data
            fecha_cita = form.fecha_cita.data
            cita = form.cita.data
            observacion = form.observacion.data

            if not dni:
                dni = cuit[2:10]
            elif not cuit:
                cuit = generar_cuil_cuit(dni, genero)

            nuevo_cliente = Personas(descripcion_nombre=descripcion_nombre,
                                    genero = genero,
                                    tipo_persona=tipo_persona,
                                    correo_electronico=correo_electronico,
                                    telefono=telefono,
                                    dni=dni,
                                    cuit=cuit,
                                    direccion=direccion,
                                    id_localidad=localidad[0])

            nueva_gestion = Gestiones(origen = origen,
                                    fecha_inicio_gestion = fecha_inicio_gestion,
                                    id_tipo_gestion = id_tipo_gestion,
                                    fecha_cita  = fecha_cita,
                                    cita = cita,
                                    usuario_alta = current_user.username
                                    )
            
            
            observacion_gestion = Observaciones(
                observacion = observacion,
                usuario_alta = current_user.username

            )
            
            if observacion and observacion.strip():
                nueva_gestion.observaciones.append(observacion_gestion)            
            tareas_por_tipo_gestion= TiposGestiones.get_first_by_id(id_tipo_gestion)
            for tarea_por_tipo_gestion in tareas_por_tipo_gestion.tareas:
                nueva_gestion_de_tarea = GestionesDeTareas(id_tarea = tarea_por_tipo_gestion.id,
                                                        usuario_alta = current_user.username,
                                                        )
                nueva_gestion.gestiones_de_tareas.append(nueva_gestion_de_tarea)

            nuevo_cliente.titular_gestion.append(nueva_gestion)
            nuevo_cliente.save()

            flash("Se ha creado la gestion correctamente.", "alert-success")
            return redirect(url_for('consultas.caratula', id_gestion = nueva_gestion.id))
        
    else:
        persona = Personas.get_by_id(id_cliente)
        con_persona = True
        if form.validate_on_submit():
            form.populate_obj(persona)
            origen = form.origen.data
            fecha_inicio_gestion = form.fecha_inicio_gestion.data
            id_tipo_gestion = form.id_tipo_gestion.data
            fecha_cita = form.fecha_cita.data
            cita = form.cita.data
            observacion = form.observacion.data

            nueva_gestion = Gestiones(origen = origen,
                                    fecha_inicio_gestion = fecha_inicio_gestion,
                                    id_tipo_gestion = id_tipo_gestion,
                                    fecha_cita  = fecha_cita,
                                    cita = cita,
                                    usuario_alta = current_user.username
                                    )
            observacion_gestion = Observaciones(
                observacion = observacion,
                usuario_alta = current_user.username

            )

            if observacion:
                nueva_gestion.observaciones.append(observacion_gestion)
            
            tareas_por_tipo_gestion= TiposGestiones.get_first_by_id(id_tipo_gestion)
            for tarea_por_tipo_gestion in tareas_por_tipo_gestion.tareas:
                nueva_gestion_de_tarea = GestionesDeTareas(id_tarea = tarea_por_tipo_gestion.id,
                                                        usuario_alta = current_user.username,
                                                        )
                nueva_gestion.gestiones_de_tareas.append(nueva_gestion_de_tarea)
            persona.titular_gestion.append(nueva_gestion)
            persona.save()

            flash("Se ha creado la gestion correctamente.", "alert-success")
            return redirect(url_for('consultas.caratula', id_gestion = nueva_gestion.id))
    return render_template("gestiones/alta_gestiones.html", form=form, origen_gestion=origen_gestion, localidades=localidades, con_persona=con_persona)

@gestiones_bp.route("/gestiones/gestiones/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def gestiones():
    criterio = request.args.get('criterio','')
    
    form = BusquedaForm()
    lista_de_personas = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("gestiones.gestiones", criterio = buscar))
    if criterio.isdigit() == True:
        lista_de_personas = Personas.get_by_cuit(criterio)
        if lista_de_personas:
            return redirect(url_for('gestiones.alta_gestiones', id_cliente = lista_de_personas.id))
        else:
            return redirect(url_for('gestiones.alta_gestiones', id_cliente = None))
    elif criterio == "":
        pass
    else:
        lista_de_personas = Personas.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_de_personas.items) == 0:
            lista_de_personas =[]

    return render_template("gestiones/gestiones.html", form = form, criterio = criterio, lista_de_personas= lista_de_personas )

@gestiones_bp.route("/gestiones/altacobroscabecera/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
@nocache
def alta_cobros_cabecera():
    id_gestion = request.args.get('id_gestion','')
    if not id_gestion:
        return redirect(url_for('consultas.lista_gestiones'))
    form = CobrosForm()                                                                                                                   
    cobros = Cobros.get_all_by_id_gestion(id_gestion)
    if cobros:
        flash('No puede crear un nuevo presupuesto porque ya existe','alert-warning')
        return redirect(url_for('consultas.cobro', id_gestion = id_gestion))
    
    if form.validate_on_submit():
        importe_total = form.importe_total.data
        moneda = form.moneda.data        
        observacion = form.observacion.data
        
        nuevo_cobro = Cobros(id_gestion=id_gestion, 
                             importe_total = importe_total,
                             moneda = moneda,
                             usuario_alta = current_user.username)        
        observacion_cobro_cabecera = Observaciones(
            id_gestion = id_gestion,
            observacion = observacion,
            usuario_alta = current_user.username)

        if observacion:
            nuevo_cobro.observaciones.append(observacion_cobro_cabecera)
        nuevo_cobro.cobro = nuevo_cobro
        nuevo_cobro.save()

        flash("El cobro se ha proyectado correctamente.", "alert-success")
        return redirect(url_for('consultas.lista_gestiones', criterio = id_gestion))
    return render_template("gestiones/cobros_cabecera.html", form = form, cobros = cobros)

@gestiones_bp.route("/gestiones/modificacobroscabecera/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def modifica_cobros_cabecera():
    id_gestion = request.args.get('id_gestion','')
    if not id_gestion:
        return redirect(url_for('consultas.lista_gestiones'))
    form = CobrosForm()                                                                                                                   
    cobro_gestion = Gestiones.get_by_id(id_gestion)
    importe_actual = cobro_gestion.cobro.importe_total
    if form.validate_on_submit():
        form.populate_obj(cobro_gestion.cobro)
        cobro_gestion.cobro.usuario_modificacion = current_user.username
        observacion = form.observacion.data
        
        #guardo una observación fija para que quede registro que se modificó si se modificó el monto
        if importe_actual != form.importe_total.data:
            observacion_cobro_cabecera_fija = Observaciones(
                id_gestion = id_gestion,
                observacion =  f'Se actualizó el presupuesto de: ${importe_actual} a ${form.importe_total.data}',
                usuario_alta = current_user.username)       
            cobro_gestion.cobro.observaciones.append(observacion_cobro_cabecera_fija)
            
        #si se guardó una observación la guardo.
        if observacion:
            observacion_cobro_cabecera = Observaciones(
            id_gestion = id_gestion,
            observacion = observacion,
            usuario_alta = current_user.username)

            cobro_gestion.cobro.observaciones.append(observacion_cobro_cabecera)
        #actualizo el importe cobrado para que no pinche
        if cobro_gestion.cobro.importes_cobros:
            cobro_gestion.cobro.importe_cobrado = sum(importe_cobro.importe for importe_cobro in cobro_gestion.cobro.importes_cobros)
            #valido que no se esté cargando un importe menor a lo ya cobrado
            if cobro_gestion.cobro.importe_cobrado > form.importe_total.data:
                flash("El nuevo importe no puede ser menor a lo ya cobrado.", "alert-danger")
                return redirect(url_for('gestiones.modifica_cobros_cabecera', id_gestion = id_gestion))
        
        cobro_gestion.save()

        flash("El la proyección de cobro de ha actualizado correctamente.", "alert-success")
        return redirect(url_for('consultas.lista_gestiones', id_gestion = id_gestion))
    return render_template("gestiones/cobros_cabecera.html", form = form, cobro_gestion=cobro_gestion)


@gestiones_bp.route("/gestiones/altacobros/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
@nocache
def alta_importe_cobro():
    id_gestion = request.args.get('id_gestion','')
    if not id_gestion:
         return redirect(url_for('consultas.lista_gestiones'))
    form = ImportesCobrosForm()                                                                                                                   
    cabecera_cobro = Gestiones.get_by_id(id_gestion)
    hoy = datetime.today()
    importes_cobrados = sum(importe_cobro.importe for importe_cobro in cabecera_cobro.cobro.importes_cobros)
    
    if form.validate_on_submit():
        fecha_cobro = form.fecha_cobro.data
        importe = form.importe.data
        tipo_cambio = form.tipo_cambio.data
        moneda = form.moneda.data
        medio_cobro = form.medio_cobro.data
        observacion = form.observacion.data
        
        nuevo_importe_cobro = ImportesCobros(
                                fecha_cobro = fecha_cobro,
                                importe = importe,
                                tipo_cambio = tipo_cambio,
                                moneda = moneda,
                                medio_cobro = medio_cobro,
                                usuario_alta = current_user.username)
        
        #valido que no se esté cargando un un pago superior a lo presupuestado
        if float(importes_cobrados) + importe > cabecera_cobro.cobro.importe_total:
            flash("El importe cobrado no puede superar al importe presupuestado, no se ha guardado el cobro.", "alert-danger")
            return redirect(url_for('consultas.cobro', id_gestion=id_gestion )) 
        
        cabecera_cobro.cobro.importe_cobrado = float(importes_cobrados) + importe
        #si se cargó una observación la guardo
        if observacion:
            observacion_importe_cobro = Observaciones(
                                                        id_gestion = cabecera_cobro.id,
                                                        id_cobro = cabecera_cobro.cobro.id,
                                                        observacion = observacion,
                                                        usuario_alta = current_user.username
                                                    )
            nuevo_importe_cobro.observaciones.append(observacion_importe_cobro)
        cabecera_cobro.cobro.importes_cobros.append(nuevo_importe_cobro)
        
        cabecera_cobro.save()

        flash("El importe se ha cargado correctamente.", "alert-success")
        return redirect(url_for('consultas.cobro', id_gestion=id_gestion ))
    return render_template("gestiones/importe_cobro.html", form=form, hoy=hoy)

@gestiones_bp.route("/gestiones/modificacioncobros/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
@nocache
def modificacion_importe_cobro():
    id_cobro_individual = request.args.get('id_cobro_individual','')
    if not id_cobro_individual:
         return redirect(url_for('consultas.lista_gestiones'))
    cobro_individual = ImportesCobros.get_by_id_cobro(id_cobro_individual)
    form = ImportesCobrosForm(obj=cobro_individual)                                                                                                                   
    id_gestion = cobro_individual.cobro.id_gestion
    hoy = datetime.today()
    importe_actual = cobro_individual.importe
    
    if form.validate_on_submit():
        form.populate_obj(cobro_individual)  # Actualizar la gestión con los datos del formulario
        cobro_individual.usuario_modificacion = current_user.username
        observacion = form.observacion.data
        
        #calculo los importes cobrados para actualizar la tabla cabecera en importe cobrado
        cabecera_cobro = Gestiones.get_by_id(id_gestion)
        importes_cobrados = sum(float(importe_cobro.importe) for importe_cobro in cabecera_cobro.cobro.importes_cobros)
        
        #valido que no se esté cargando un pago superior a lo presupuestado
        if float(importes_cobrados) + form.importe.data > cobro_individual.cobro.importe_total:
            flash("El importe cobrado no puede superar al importe presupuestado, no se ha guardado el cobro.", "alert-danger")
            return redirect(url_for('consultas.cobro', id_gestion =id_gestion )) 
        
        #valido que para que grabe la observacion fija haya alguna modificacion en los importes
        if importe_actual != form.importe.data:
            observacion_importe_cobro_fijo =Observaciones(
                                                    id_gestion = cobro_individual.cobro.id_gestion,
                                                    id_cobro = cobro_individual.cobro.id,
                                                    observacion =  f'Se actualizó el cobro de: ${importe_actual} a ${form.importe.data}',
                                                    usuario_alta = current_user.username)
            cobro_individual.observaciones.append(observacion_importe_cobro_fijo)
        
        #cobro_individual.cobro.importe_cobrado = float(importes_cobrados) + form.importe.data
        if observacion:
            observacion_importe_cobro = Observaciones(
                                                        id_gestion = cobro_individual.cobro.id_gestion,
                                                        id_cobro = cobro_individual.cobro.id,
                                                        observacion = observacion,
                                                        usuario_alta = current_user.username
                                                    )
            cobro_individual.observaciones.append(observacion_importe_cobro)
        
        cobro_individual.save()
        cabecera_cobro.cobro.importe_cobrado =importes_cobrados
        cabecera_cobro.save()

        flash("El importe se ha cargado correctamente.", "alert-success")
        return redirect(url_for('consultas.ver_cobros', id_gestion=id_gestion ))
    return render_template("gestiones/importe_cobro.html", form=form, cobro_individual=cobro_individual, hoy=hoy)

@gestiones_bp.route("/gestiones/modificaciongestiones/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def modificacion_gestiones():
    id_gestion = request.args.get('id_gestion','')
    if not id_gestion:
        return redirect(url_for('gestiones.gestiones'))
    gestion = Gestiones.get_by_id(id_gestion)
    print (gestion.personas.localidades.localidad)
    form = AltaGestionesForm(obj=gestion)                                                                                                                   
    clientes = Personas.get_all()
    form.id_tipo_gestion.choices = tipo_gestion_select()

    if form.validate_on_submit():
        form.populate_obj(gestion)  # Actualizar la gestión con los datos del formulario
        gestion.usuario_modificacion = current_user.username
        observacion = form.observacion.data
        
        observacion_gestion = Observaciones(
            observacion = observacion,
            usuario_alta = current_user.username
        )

        if observacion:
            gestion.observaciones.append(observacion_gestion)
        gestion.save()
    
        flash("Se ha modificado la gestion correctamente.", "alert-success")
        return redirect(url_for('consultas.caratula', id_gestion = gestion.id))
       
    # for campo in list(request.form.items())[1:11]:
    #     data_campo = getattr(form,campo[0]).data
    #     #valido que que estos campos no queden string porque da error autoflush no agrego id_dibujante porque lo tengo que sacar de acá-
    #     if campo[0] == 'id_tipo_gestion' and data_campo == '':
    #         data_campo = None
    #         setattr(gestion,campo[0], data_campo)
    #     else:
    #         setattr(gestion,campo[0], data_campo)

    return render_template("gestiones/modificacion_gestiones.html", form = form, clientes = clientes, gestion = gestion)

@gestiones_bp.route("/gestiones/nuevopaso/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def nuevo_paso():
    id_gestion = request.args.get('id_gestion','')
    form = PasoForm()
    gestion = Gestiones.get_by_id(id_gestion)

    if form.validate_on_submit():

        observacion = form.observacion.data
        
        observacion_gestion = Observaciones(
            observacion = observacion,
            usuario_alta = current_user.username

        )

        if observacion:
            gestion.observaciones.append(observacion_gestion)
        gestion.save()
        flash("Se ha dado de alta un paso en la bitácora correctamente.", "alert-success")
        return redirect(url_for('consultas.bitacora', id_gestion = id_gestion))
    
    return render_template("gestiones/nuevo_paso.html", form = form,  gestion = gestion)

@gestiones_bp.route("/gestiones/gestionestareas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def gestiones_tareas():
    id_gestion = request.args.get('id_gestion','')

    form = GestionesTareasForm()
    form.id_tarea.choices = tareas_select(id_gestion)
    gestion = Gestiones.get_by_id(id_gestion)
    
    if form.validate_on_submit():

        id_tarea = form.id_tarea.data
        nueva_gestion_de_tarea = GestionesDeTareas(id_tarea = id_tarea,
                                                       usuario_alta = current_user.username,
                                                       )
        gestion.gestiones_de_tareas.append(nueva_gestion_de_tarea)
        gestion.save()
        
        flash('Tarea incorporada correctamente.','alert-success')
        return redirect(url_for('gestiones.gestiones_tareas', id_gestion = id_gestion))
    
    return render_template("gestiones/gestiones_tareas.html", form = form,  gestion = gestion)

@gestiones_bp.route("/gestiones/detallegxt/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def detalle_gdt():
    id_gestion_de_tarea = request.args.get('id_gestion_de_tarea','')

    hoy = datetime.today()
    gestion_de_tarea = GestionesDeTareas.get_all_by_id_gestion_de_tarea(id_gestion_de_tarea)
    gestion = None

    form = DetallesGdTForm(obj=gestion_de_tarea)
    observaciones_gestion_tareas = Observaciones.get_all_by_id_gestion_de_tarea(id_gestion_de_tarea)
   
    if form.validate_on_submit():
        form.populate_obj(gestion_de_tarea) 
        gestion_de_tarea.usuario_modificacion = current_user.username
        observacion = form.observacion.data 
        
        observacion_gestion = Observaciones(
            id_gestion = gestion_de_tarea.id_gestion,
            observacion = observacion,
            usuario_alta = current_user.username
        )

        if observacion:
            gestion_de_tarea.observaciones.append(observacion_gestion)
        gestion_de_tarea.save()
        
        flash('Tarea actualizada correctamente.','alert-success')
        return redirect(url_for('consultas.tareas_pendientes', id_gestion=gestion_de_tarea.id_gestion))
    
    for campo in list(request.form.items())[2:]:
        data_campo = getattr(form,campo[0]).data
        setattr(gestion_de_tarea,campo[0], data_campo)
    return render_template("gestiones/detalle_gdt.html", 
                           form=form, 
                           gestion_de_tarea=gestion_de_tarea, 
                           observaciones_gestion_tareas=observaciones_gestion_tareas, 
                           gestion=gestion,
                           hoy=hoy)


@gestiones_bp.route("/gestiones/documentos/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def nuevo_documento():
  
    id_gestion = request.args.get('id_gestion','')
    id_modelo_documento = request.args.get('id_modelo_documento','')
    form = DocumentosForm()
        
    gestion = Gestiones.get_by_id(id_gestion)
    form.id_modelo_documento.choices = modelos_documentos_select()
    if form.validate_on_submit():
        if not form.texto.data:
            id_modelo_documento = form.id_modelo_documento.data
            return redirect(url_for('gestiones.nuevo_documento', id_modelo_documento=id_modelo_documento, id_gestion=id_gestion))
        else:
            documento= ModelosDocumentos.get_first_by_id(int(id_modelo_documento))
            texto = form.texto.data
            nuevo_documento = Documentos(id_tipo_documento = documento.id_tipo_documento,
                                         texto = texto,
                                         usuario_alta = current_user.username,
                                         usuario_modificacion = current_user.username)
            gestion.documentos.append(nuevo_documento)
            gestion.save()
            flash("Se ha dado de alta un documento correctamente", "alert-success")
            return redirect(url_for('consultas.lista_gestiones'))
    if id_modelo_documento: 
        documento = ModelosDocumentos.get_first_by_id(id_modelo_documento)
        campos_disponibles = VariablesDocumentos.get_variables()
        documento_formateado = renderizar_modelo_con_instancia(campos_disponibles, documento.texto, gestion )
        return render_template("gestiones/documentos.html", form = form,  documento_formateado=documento_formateado, gestion = gestion, documento=documento)    
        
    return render_template("gestiones/documentos.html", form = form,  gestion = gestion)
