from rest_framework import serializers # Proporciona herramientas para convertir datos complejos como los modelos de Django a tipos de datos nativos de Python 
from apps.reservas.models import Reserva # Importmaos el modelo de Reservas

class ReservaSerializer(serializers.ModelSerializer):
    class Meta: # Esta es una clase interna Meta donde definimos el comportamiento del serializador.
        model = Reserva # Aquí indicamos cuál es el modelo que queremos serializar/deserializar.
        # 'fields' define qué campos del modelo serán incluidos en la serialización.
        # '__all__' es una manera abreviada de decir que queremos incluir todos los campos del modelo 'Evento'.
        fields = '__all__'