import json
import boto3
import time
from botocore.exceptions import ClientError
from decimal import Decimal

# Inicializar el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = 'IOT' 
table = dynamodb.Table(table_name)

# Función para serializar objetos no compatibles con JSON
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # O usa str(obj) si prefieres conservar precisión como texto
    raise TypeError(f"Tipo no serializable: {type(obj)}")

def lambda_handler(event, context):
    try:
        # Extraer parámetros de la query string
        query_params = event.get('queryStringParameters', {})
        gas_value = query_params.get('gas_value')
        flama_value = query_params.get('flama_value')
        
        # Validar que los parámetros existan
        if gas_value is None or flama_value is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Parámetros faltantes: gas_value o flama_value'})
            }
        
        # Preparar el elemento para DynamoDB
        item = {
            'IOT': str(int(time.time())),  # ID único basado en timestamp
            'IOT123': str(int(time.time())),
            'gas_value': Decimal(gas_value),  # Convertir a Decimal
            'flama_value': int(flama_value),
            'timestamp': Decimal(str(time.time()))  # Convertir a Decimal (como string para evitar pérdida de precisión)
        }
        
        # Guardar el elemento en DynamoDB
        table.put_item(Item=item)
        
        # Responder exitosamente
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Datos almacenados exitosamente', 'item': item}, default=decimal_default)
        }
    
    except ClientError as e:
        print(f"Error al guardar en DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error al guardar en DynamoDB', 'error': str(e)})
        }
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error inesperado', 'error': str(e)})
        }