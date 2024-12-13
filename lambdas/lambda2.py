import json
import boto3
import csv
from io import StringIO
from decimal import Decimal

# Inicializar clientes
s3 = boto3.client('s3')

# Configurar nombres de recursos
bucket_name = 'nombre-de-tu-bucket-s3'
file_name = 'datos_dynamo.csv'

def decimal_default(obj):
    """ Función para serializar Decimal a flotante. """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo no serializable: {type(obj)}")

def lambda_handler(event, context):
    """
    Procesar eventos de DynamoDB Streams y guardar datos en un archivo CSV en S3.
    """
    try:
        # Inicializar buffer CSV
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        # Descargar archivo existente de S3 si existe
        try:
            existing_file = s3.get_object(Bucket=bucket_name, Key=file_name)
            existing_data = existing_file['Body'].read().decode('utf-8')
            
            # Copiar datos existentes al nuevo archivo
            csv_buffer.write(existing_data)
        except s3.exceptions.NoSuchKey:
            # Si el archivo no existe, escribir la cabecera
            csv_writer.writerow(['gas_value', 'flama_value', 'timestamp'])
        
        # Procesar cada registro del evento de DynamoDB Streams
        for record in event['Records']:
            # Asegurarse de que el evento sea de inserción
            if record['eventName'] == 'INSERT':
                # Extraer el nuevo valor del evento
                new_image = record['dynamodb']['NewImage']
                gas_value = decimal_default(new_image['gas_value'])
                flama_value = int(new_image['flama_value']['N'])
                timestamp = decimal_default(new_image['timestamp'])
                
                # Escribir el nuevo registro en el archivo CSV
                csv_writer.writerow([gas_value, flama_value, timestamp])
        
        # Subir el nuevo archivo CSV a S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=csv_buffer.getvalue()
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Datos procesados y almacenados en S3'})
        }
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error inesperado', 'error': str(e)})
        }