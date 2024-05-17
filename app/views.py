from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import RedDePetri, ArcosEntradas, ArcosSalidas, Transiciones, Lugares
# Create your views here.

def index(request):
    return render(request, 'pages/index.html',
    {
    })

def Procesos(red):
    procesos = RedDePetri.objects.filter(id=red)
# Mostrar las transiciones disponibles
    arcosEntradas = ArcosEntradas.objects.all()
    transicion = Transiciones.objects.all()
    numPlazas = 0
    plazasActivas = 0
    for t in transicion: # Revisar todas las transiciones
        arcos = ArcosEntradas.objects.filter(destino=t.id)  # Revisar solo los arcos d la transicion
        
        for p in arcos: # verificar si estas plazas esta listas
            numPlazas += 1 # numero de plazas
            plaza = Lugares.objects.get(id=p.origen.id) 
            if p.peso <= plaza.tokens:
                plazasActivas += 1 # numero de plazas activas
        if numPlazas == plazasActivas:
            t.habilitada = True
            t.save()
        else:
            t.habilitada = False
            t.save()
        numPlazas = 0
        plazasActivas = 0
# Salida en pantalla
   

def ProcesosEjecucion(request, transicion):
    
   
    transicionActiva = Transiciones.objects.filter(id=transicion)

         # La transicion activada
    # Generar tokens de salida
    arcosSalidas = ArcosSalidas.objects.filter(origen=transicion)
    for p in arcosSalidas:
        plaza = Lugares.objects.get(id=p.destino.id)
        plaza.tokens += p.peso
        plaza.save()
    # Remover tokens consumidos
    arcosEntradas = ArcosEntradas.objects.filter(destino=transicion)
    for p in arcosEntradas:
        plaza = Lugares.objects.get(id=p.origen.id)
        plaza.tokens -= p.peso
        plaza.save()

# Mostrar las transiciones disponibles
    arcosEntradas = ArcosEntradas.objects.all()
    transicion = Transiciones.objects.all()
    numPlazas = 0
    plazasActivas = 0
    for t in transicion: # Revisar todas las transiciones
        arcos = ArcosEntradas.objects.filter(destino=t.id)  # Revisar solo los arcos d la transicion
        for p in arcos: # verificar si estas plazas esta listas
            numPlazas += 1 # numero de plazas
            plaza = Lugares.objects.get(id=p.origen.id) 
            if p.peso <= plaza.tokens:
                plazasActivas += 1 # numero de plazas activas
        if numPlazas == plazasActivas:
            t.habilitada = True
            t.save()
        else:
            t.habilitada = False
            t.save()
        numPlazas = 0
        plazasActivas = 0
# Salida en pantalla  
    return render(request, 'pages/procesosEjecucion.html',
    {
        
        'transicion' : transicionActiva,
        'numPlazas' : numPlazas,
        'plazasActivas' : plazasActivas,
        
    })


def Solicitud(request):
    # Valores para la lista desplegable
    
    opciones = RedDePetri.objects.exclude(nombre="Planificador").values_list('nombre', flat=True)
    red = RedDePetri.objects.filter(nombre="Planificador")
    planificador = red[0]

    eliminar(planificador.id)

    # Si el formulario ha sido enviado
    if request.method == 'POST':
        # Obtener los datos del formulario
        valor_lista = request.POST.get('producto')
        valor_input = request.POST.get('campo_input')
        transicion_id = request.POST.get('transicion_id')
        print(transicion_id)
        
    
        

        # Realizar acciones con los datos recibidos
        print("Valor de la lista desplegable:", valor_lista)
        print("Valor del campo input:", valor_input)
        return redirect(reverse('estatus', args=(planificador.id,valor_lista,)))

    return render(request, 'pages/solicitud.html', {'opciones': opciones, 'red':planificador})


def list_sol(request):
    return render(request, 'pages/list_solicitudes.html',
    {
    })

def estatus(request,red,producto):
    
    lugares = Lugares.objects.all()
    Modelo = RedDePetri.objects.filter(nombre=producto)
    print(Modelo[0].nombre)
    lugares_p = Modelo[0].lugares.all()
    
    red_petri = RedDePetri.objects.get(id=red)

    # Filtra las transiciones relacionadas con esa red de Petri
    transiciones_habilitadas = red_petri.transiciones.filter(habilitada=True)
    
    Equipos_plaza = red_petri.lugares.filter(nombre = "Analisis Equipos")
    Insumo_plaza = red_petri.lugares.filter(nombre = "Analisis Insumos")
    Recepcion_plaza = red_petri.lugares.filter(nombre = "Recepcion")
    Aceptacion_plaza = red_petri.lugares.filter(nombre = "Orden Aceptada")
    
    
    
    if Aceptacion_plaza[0].tokens == 1:
        print("Entre en acepacion")
        redirect(reverse('estatus', args=(red,producto,)))
        transiciones_produccion = Modelo[0].transiciones.filter(habilitada=True)
        print(transiciones_produccion[0].nombre)
        while len(transiciones_produccion) > 0:
            
            Ejecucion(transiciones_produccion[0].id,Modelo[0].id,producto)
            transiciones_produccion = Modelo[0].transiciones.filter(habilitada=True)
            

        

    if Equipos_plaza[0].tokens == 1:
        if True:
                for t in transiciones_habilitadas:
                    if t.nombre == "si equipo":
                        Ejecucion(t.id,red,producto)
        else:
                 for t in transiciones_habilitadas:
                    if t.nombre == "no equipo":
                        Ejecucion(t.id,red,producto)
    
    if Insumo_plaza[0].tokens == 1:
        if True:
                for t in transiciones_habilitadas:
                    if t.nombre == "si insumo":
                        Ejecucion(t.id,red,producto)
        else:
                 for t in transiciones_habilitadas:
                    if t.nombre == "no insumo":
                        Ejecucion(t.id,red,producto)

    if Recepcion_plaza[0].tokens == 1:
          print("recepcion")
          if Modelo:
                for t in transiciones_habilitadas:
                    if t.nombre == "analisis":
                        print(t.nombre)
                        Ejecucion(t.id,red,producto)
          else:
                for t in transiciones_habilitadas:
                    if t.nombre == "sin Modelo":
                        Ejecucion(t.id,red,producto)


 
    if len(transiciones_habilitadas) == 1:
        Ejecucion(transiciones_habilitadas[0].id,red,producto)
    

    return render(request, 'pages/estatus.html',
    {
        'p':lugares,'l_p':lugares_p
    })

def Ejecucion(transicion,red,producto):
    
    red_petri = RedDePetri.objects.filter(id=red)
    transicionActiva = Transiciones.objects.filter(id=transicion)

         # La transicion activada
    # Generar tokens de salida
    arcosSalidas = ArcosSalidas.objects.filter(origen=transicion)
    for p in arcosSalidas:
        plaza = Lugares.objects.get(id=p.destino.id)
        plaza.tokens += p.peso
        plaza.save()
    # Remover tokens consumidos
    arcosEntradas = ArcosEntradas.objects.filter(destino=transicion)
    for p in arcosEntradas:
        plaza = Lugares.objects.get(id=p.origen.id)
        plaza.tokens -= p.peso
        plaza.save()

# Mostrar las transiciones disponibles
    arcosEntradas = ArcosEntradas.objects.all()
    transicion = Transiciones.objects.all()
    numPlazas = 0
    plazasActivas = 0
    for t in transicion: # Revisar todas las transiciones
        arcos = ArcosEntradas.objects.filter(destino=t.id)  # Revisar solo los arcos d la transicion
        for p in arcos: # verificar si estas plazas esta listas
            numPlazas += 1 # numero de plazas
            plaza = Lugares.objects.get(id=p.origen.id) 
            if p.peso <= plaza.tokens:
                plazasActivas += 1 # numero de plazas activas
        if numPlazas == plazasActivas:
            t.habilitada = True
            t.save()
        else:
            t.habilitada = False
            t.save()
        numPlazas = 0
        plazasActivas = 0

        
        redirect(reverse('estatus', args=(red,producto,)))
# Salida en pantalla  
   
def eliminar(red):
    red_petri = RedDePetri.objects.get(id=red)

    # Filtra las transiciones relacionadas con esa red de Petri
    lugares = red_petri.lugares.all()
    for l in lugares:
        if l.nombre != "Inicio":
            l.tokens = 0
            l.save()
            print(l.nombre)
            
        else:
            l.tokens = 1
            l.save()
    Procesos(red)