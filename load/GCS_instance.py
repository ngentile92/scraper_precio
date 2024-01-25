from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import time

def get_sql_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('sqladmin', 'v1beta4', credentials=credentials)

def start_instance(project_id, instance_id):
    service = get_sql_service()
    request = service.instances().start(project=project_id, instance=instance_id)
    response = request.execute()
    print(f'Starting instance: {instance_id}')
    # Puedes añadir aquí lógica adicional para verificar el estado de la instancia

def stop_instance(project_id, instance_id):
    service = get_sql_service()
    request = service.instances().stop(project=project_id, instance=instance_id)
    response = request.execute()
    print(f'Stopping instance: {instance_id}')
    # Puedes añadir aquí lógica adicional para verificar el estado de la instancia

# Uso de las funciones
project_id = 'tu-project-id'
instance_id = 'tu-instance-id'

# Iniciar la instancia
start_instance(project_id, instance_id)

# Aquí tu lógica principal (procesamiento de datos, etc.)

# Detener la instancia
stop_instance(project_id, instance_id)
