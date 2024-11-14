import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_funciones = dynamodb.Table('t_funciones')
    t_usuarios = dynamodb.Table('t_usuarios')
    
    # Verificar permisos del usuario
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    # Consultar el rol del usuario
    user_response = t_usuarios.get_item(Key={'user_id': user_id})
    if 'Item' not in user_response or user_response['Item'].get('role') != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }
    
    # Obtener los datos necesarios para eliminar la función
    cinema_id = event.get('cinema_id')
    show_id = event.get('show_id')
    
    # Validación de entrada
    if not cinema_id or not show_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and show_id are required'})
        }
    
    # Eliminar la función completa
    try:
        t_funciones.delete_item(
            Key={
                'cinema_id': cinema_id,
                'show_id': show_id
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Function deleted successfully'})
        }
    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
