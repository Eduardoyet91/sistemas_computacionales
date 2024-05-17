from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('procesos/<str:red>', views.Procesos, name='procesos'),
    path('solicitud', views.Solicitud, name='solicitud'),
    path('list', views.list_sol, name='lista'),
    path('status/<str:red>/<str:producto>', views.estatus, name='estatus'),
    path('pEjecucion/<str:transicion>', views.ProcesosEjecucion, name='pEjecucion'),
]
