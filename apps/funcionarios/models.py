from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class Base(models.Model):
    creacion = models.DateField(auto_now=True)
    actualizacion = models.DateField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        abstract = True

class TipoDocumento(Base):

    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Cargo(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Dependencia(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Implemento(Base):
    nombre = models.CharField(max_length=50)

class Espacio(Base):
    nombre = models.CharField(max_length=50)
    
class Area(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class Linea(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class Ambiente(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class Genero(Base):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre
    
class Visita(Base):
    fecha_inicio = models.DateTimeField()
    fecha_finalizacion = models.DateTimeField()
    discapacidad = models.CharField(max_length=50)
    procedencia = models.CharField(max_length=80)
    grabacion  = models.BooleanField(default=True)

# Modelo personalizado
class PersonaManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)

        if password:
            user.set_password(password)
        else:
            raise ValueError('El campo contraseña es obligatorio')

        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(correo, password, **extra_fields)

class Persona(AbstractBaseUser, Base):
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    id_tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, null=True)
    identificacion = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=10)
    correo = models.EmailField(unique=True)
    id_cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, null=True)
    id_dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE, null=True)
    id_implemento = models.ForeignKey(Implemento, on_delete=models.CASCADE, null=True)
    id_visita = models.ForeignKey(Visita, on_delete=models.CASCADE, null=True)
    id_genero = models.ForeignKey(Genero, on_delete=models.CASCADE, null=True)
    id_area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    id_linea = models.ForeignKey(Linea, on_delete=models.CASCADE, null=True)
    id_ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, null=True)
    id_espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, null=True)
    imagen_perfil = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_active = models.BooleanField("Habilitado", default=True)
    is_staff = models.BooleanField("Acceso al admin", default=False)
    is_superuser = models.BooleanField("Acceso al admin", default=False)
    is_admin = models.BooleanField("Acceso al admin", default=False)
    objects = PersonaManager()

    USERNAME_FIELD = 'correo' # Campo utilizado para identificar a los usuarios al iniciar sesión
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'id_tipo_documento', 'identificacion', 'telefono', 'id_cargo', 'id_dependencia',]

    def __str__(self):
            return self.correo

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

