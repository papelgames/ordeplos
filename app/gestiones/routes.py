import logging

import os
from time import ctime
from datetime import date, datetime, timedelta

from flask import render_template, redirect, url_for, current_app, flash, send_file, request #, make_response, abort
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import Personas, TiposGestiones, TiposBienes, Gestiones, Observaciones, Cobros, ImportesCobros, Tareas, GestionesDeTareas
from . import gestiones_bp 
from .forms import AltaGestionesForm, BusquedaForm, CobrosForm, ImportesCobrosForm, PasoForm, GestionesTareasForm, DetallesGdTForm, DetallesGdTDibujanteForm

from app.common.mail import send_email

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

#creo una tupla para usar en el campo select del form que quiera que necesite los tipo de bienes
def tipo_bien_select():
    tipos_bienes = TiposBienes.get_all()
    select_tipo_bien =[( '','Seleccionar tipo de bien')]
    for rs in tipos_bienes:
        sub_select_tipo_bien = (str(rs.id), rs.descripcion)
        select_tipo_bien.append(sub_select_tipo_bien)
    return select_tipo_bien

#creo una tupla para usar en el campo select del form que quiera que necesite las tareas
def tareas_select(id_gestion):
    tareas = Tareas.get_tareas_no_relacionadas(id_gestion)
    select_tareas =[(0,'Seleccionar Tarea')]
    for rs in tareas:
        sub_select_tareas = (rs.id, rs.descripcion)
        select_tareas.append(sub_select_tareas)
    return select_tareas

@gestiones_bp.route("/gestiones/altagestiones/<int:id_cliente>", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_gestiones(id_cliente):
    if not id_cliente:
        return redirect(url_for('gestiones.gestiones'))
    form = AltaGestionesForm()                                                                                                                   
    clientes = Personas.get_all()
    form.id_tipo_gestion.choices = tipo_gestion_select()
    form.id_tipo_bienes.choices = tipo_bien_select()
    hoy = datetime.today()
    q_dias_para_medicion = current_app.config['DIAS_MEDICION']
    fecha_probable_medicion_default= hoy + timedelta(days=q_dias_para_medicion)

    if form.validate_on_submit():
        titular = form.titular.data
        ubicacion_gestion = form.ubicacion_gestion.data 
        coordenadas = form.coordenadas.data
        id_tipo_bienes = form.id_tipo_bienes.data
        fecha_inicio_gestion = form.fecha_inicio_gestion.data
        fecha_probable_medicion = form.fecha_probable_medicion.data
        id_tipo_gestion = form.id_tipo_gestion.data
        numero_partido = form.numero_partido.data
        numero_partida = form.numero_partida.data
        nomenclatura = form.nomenclatura.data
        observacion = form.observacion.data

        nueva_gestion = Gestiones(id_cliente = id_cliente,
                                titular = titular,
                                ubicacion_gestion = ubicacion_gestion,
                                coordenadas= coordenadas, 
                                id_tipo_bienes = id_tipo_bienes,
                                fecha_inicio_gestion = fecha_inicio_gestion,
                                fecha_probable_medicion = fecha_probable_medicion,
                                id_tipo_gestion = id_tipo_gestion,
                                numero_partido = numero_partido,
                                numero_partida = numero_partida,
                                nomenclatura = nomenclatura,
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
        nueva_gestion.save()

        flash("Se ha creado la gestion correctamente.", "alert-success")
        return redirect(url_for('consultas.caratula', id_gestion = nueva_gestion.id))
    return render_template("gestiones/alta_gestiones.html", form = form, clientes = clientes, hoy=hoy, fecha_probable_medicion_default=fecha_probable_medicion_default)

@gestiones_bp.route("/gestiones/gestiones/<criterio>", methods = ['GET', 'POST'])
@gestiones_bp.route("/gestiones/gestiones/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def gestiones(criterio = ""):
    form = BusquedaForm()
    lista_de_personas = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("gestiones.gestiones", criterio = buscar))
    if criterio.isdigit() == True:
        lista_de_personas = Personas.get_by_cuit(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_personas = Personas.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_de_personas.items) == 0:
            lista_de_personas =[]

    return render_template("gestiones/gestiones.html", form = form, criterio = criterio, lista_de_personas= lista_de_personas )

@gestiones_bp.route("/gestiones/altacobroscabecera/<int:id_gestion>", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_cobros_cabecera(id_gestion):
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
            nuevo_cobro.observaciones = observacion_cobro_cabecera
        nuevo_cobro.save()

        flash("El cobro se ha proyectado correctamente.", "alert-success")
        return redirect(url_for('consultas.lista_gestiones', criterio = id_gestion))
    return render_template("gestiones/alta_cobros_cabecera.html", form = form, cobros = cobros)

@gestiones_bp.route("/gestiones/altacobros/<int:id_cobro>", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_importe_cobro(id_cobro):
    if not id_cobro:
        return redirect(url_for('consultas.lista_gestiones'))
    form = ImportesCobrosForm()                                                                                                                   
    cabecera_cobro = Cobros.get_all_by_id_cobro(id_cobro)
    hoy = datetime.today()
    cobros = ImportesCobros.get_all_by_id_cobro(id_cobro)

    if form.validate_on_submit():
        fecha_cobro = form.fecha_cobro.data
        importe = form.importe.data
        tipo_cambio = form.tipo_cambio.data
        moneda = form.moneda.data
        medio_cobro = form.medio_cobro.data
        observacion = form.observacion.data
        
        nuevo_importe_cobro = ImportesCobros(id_cobro = id_cobro,
                             fecha_cobro = fecha_cobro,
                             importe = importe,
                             tipo_cambio = tipo_cambio,
                             moneda = moneda,
                             medio_cobro = medio_cobro,
                             usuario_alta = current_user.username)
        
        observacion_importe_cobro = Observaciones(
            id_gestion = cabecera_cobro.id_gestion,
            id_cobro = id_cobro,
            observacion = observacion,
            usuario_alta = current_user.username
        )

        if observacion:
            nuevo_importe_cobro.observaciones = observacion_importe_cobro
        nuevo_importe_cobro.save()

        flash("El importe se ha cargado correctamente.", "alert-success")
        return redirect(url_for('gestiones.alta_importe_cobro', id_cobro=id_cobro ))
    return render_template("gestiones/alta_importe_cobro.html", form=form, cobros=cobros, hoy=hoy)


@gestiones_bp.route("/gestiones/modificaciongestiones/<int:id_gestion>", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def modificacion_gestiones(id_gestion):
    if not id_gestion:
        return redirect(url_for('gestiones.gestiones'))
    gestion = Gestiones.get_by_id(id_gestion)
    form = AltaGestionesForm(obj=gestion)                                                                                                                   
    clientes = Personas.get_all()
    form.id_tipo_gestion.choices = tipo_gestion_select()
    form.id_tipo_bienes.choices = tipo_bien_select()
    
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
       
    for campo in list(request.form.items())[1:11]:
        data_campo = getattr(form,campo[0]).data
        #valido que que estos campos no queden string porque da error autoflush no agrego id_dibujante porque lo tengo que sacar de acá-
        if campo[0] == 'id_tipo_bienes' or campo[0] == 'id_tipo_gestion' and data_campo == '':
            data_campo = None
            setattr(gestion,campo[0], data_campo)
        else:
            setattr(gestion,campo[0], data_campo)

    return render_template("gestiones/modificacion_gestiones.html", form = form, clientes = clientes, gestion = gestion)

@gestiones_bp.route("/gestiones/nuevopaso/<int:id_gestion>", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def nuevo_paso(id_gestion):
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
def detalle_gdt():
    id_gestion_de_tarea = request.args.get('id_gestion_de_tarea','')

    hoy = datetime.today()
    gestion_de_tarea = GestionesDeTareas.get_all_by_id_gestion_de_tarea(id_gestion_de_tarea)
    gestion = None
    if gestion_de_tarea.tareas.carga_dibujante == True:
        form = DetallesGdTDibujanteForm(obj=gestion_de_tarea)
        gestion = Gestiones.get_by_id(gestion_de_tarea.id_gestion)
        dibujante_actual = gestion.id_dibujante
        if dibujante_actual:
            nombre_dibujante_actual = gestion.dibujante.descripcion_nombre
            correo_dibujante_actual = gestion.dibujante.correo_electronico
        carga_dibujante_valor = True
    else:
        form = DetallesGdTForm(obj=gestion_de_tarea)
        carga_dibujante_valor = False
    observaciones_gestion_tareas = Observaciones.get_all_by_id_gestion_de_tarea(id_gestion_de_tarea)

    dibujantes = Users.get_by_es_dibujante()
    
    if form.validate_on_submit():
        form.populate_obj(gestion_de_tarea) 
        gestion_de_tarea.usuario_modificacion = current_user.username
        observacion = form.observacion.data 
        
        observacion_gestion = Observaciones(
            id_gestion = gestion_de_tarea.id_gestion,
            observacion = observacion,
            usuario_alta = current_user.username
        )
        if carga_dibujante_valor: #si estamos modificando una tarea de dibujante
            id_dibujante = form.id_dibujante.data.split('|',)[0]
            
            gestion.id_dibujante = int(id_dibujante)
            gestion.usuario_modificacion = current_user.username
            gestion.save()
            observacion_dibujante = Observaciones(
                                    id_gestion = gestion_de_tarea.id_gestion,
                                    observacion = 'Se asignó al dibujante: ' + form.id_dibujante.data,
                                    usuario_alta = current_user.username
                                )
            
            gestion_de_tarea.observaciones.append(observacion_dibujante)
            #enviamos el correo avisando que se lo asigno como dibujante
            if int(id_dibujante) != dibujante_actual:
                nuevo_dibujante = Personas.get_by_id(id_dibujante)
                send_email(subject='Asignación de dibujo',
                            sender=(current_app.config['MAIL_DEFAULT_SENDER'], current_app.config['MAIL_USERNAME'] ),
                            recipients=[nuevo_dibujante.correo_electronico, ],
                            text_body=f'Hola {nuevo_dibujante.descripcion_nombre}, has sido asignado como dibujante en la gestión {gestion.id} de {gestion.titular}',
                            html_body=f'<p>Hola <strong>{nuevo_dibujante.descripcion_nombre}</strong>, has sido asignado como dibujante en la gestión {gestion.id} de {gestion.titular}</p> {observacion}')
                if dibujante_actual:
                    send_email(subject='Dibujo cancelado',
                            sender=(current_app.config['MAIL_DEFAULT_SENDER'], current_app.config['MAIL_USERNAME'] ),
                            recipients=[correo_dibujante_actual, ],
                            text_body=f'Hola {nombre_dibujante_actual}, dibujo cancelado',
                            html_body=f'<p>Hola <strong>{nombre_dibujante_actual}</strong>, el dibujo de la gestión {gestion.id} de {gestion.titular} ha sido cancelado </p> ')


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
                           carga_dibujante_valor=carga_dibujante_valor, 
                           dibujantes=dibujantes, 
                           gestion=gestion,
                           hoy=hoy)
