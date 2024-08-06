from django.contrib import admin
from .models import TipoDocumento, Cargo, Dependencia, Persona,Genero,Area,Linea,Ambiente,Asistente,VisitaAsistente,Visita

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('id_persona','fecha_inicio','fecha_finalizacion','discapacidad','procedencia','grabacion')

@admin.register(VisitaAsistente)
class VisitaAsistenteAdmin(admin.ModelAdmin):
    list_display = ('visita','asistente',)

@admin.register(Asistente)
class AsistenteAdmin(admin.ModelAdmin):
    list_display = ('nombre_asistente','apellidos_asistente','telefono_asistente','correo_asistente','id_tipo_documento_asistente','identificacion_asistente',)
@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    
@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    
@admin.register(Linea)
class LineaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    
@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'correo', 'id_tipo_documento', 'identificacion', 'telefono', 'id_cargo', 'id_dependencia','id_implemento','id_genero','id_area','id_linea','id_ambiente','id_espacio', 'is_active', 'is_staff', 'is_superuser', 'is_admin')
    search_fields = ('nombres', 'apellidos', 'correo')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_admin')
