import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_horarios = dynamodb.Table('t_horarios')
    t_usuarios = dynamodb.Table('t_usuarios')
    
    # Obtener user_id y verificar permisos
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
    
    # Obtener datos del horario de función
    cinema_id = event.get('cinema_id')
    show_id = event.get('show_id')
    movie_id = event.get('movie_id')
    hall = event.get('hall')
    start_time = event.get('start_time')
    end_time = event.get('end_time')

    # Validación de entrada
    if not all([cinema_id, show_id, movie_id, hall, start_time, end_time]):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields'})
        }
    
    # Agregar el nuevo horario
    t_horarios.put_item(
        Item={
            'cinema_id': cinema_id,
            'show_id': show_id,
            'movie_id': movie_id,
            'hall': hall,
            'start_time': start_time,
            'end_time': end_time
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Showtime added successfully'})
    }
