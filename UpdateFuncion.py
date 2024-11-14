import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_funciones = dynamodb.Table('t_funciones')  # Asegúrate de que el nombre de la tabla sea correcto
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
    
    # Obtener los identificadores clave
    cinema_id = event.get('cinema_id')
    show_id = event.get('show_id')
    
    if not cinema_id or not show_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and show_id are required'})
        }
    
    # Construir la expresión de actualización con los campos en el body
    update_expression = "SET "
    expression_values = {}
    expression_names = {}  # Inicializar como un diccionario vacío

    # Campos para actualizar
    fields_to_update = ['movie_id', 'hall', 'start_time', 'end_time']

    for field in fields_to_update:
        if event.get(field) is not None:
            # Usar alias si el nombre del campo es reservado
            if field == 'name':
                expression_names['#nm'] = field
                update_expression += "#nm = :name, "
                expression_values[":name"] = event[field]
            else:
                update_expression += f"{field} = :{field}, "
                expression_values[f":{field}"] = event[field]

    # Remover la última coma y espacio de update_expression
    update_expression = update_expression.rstrip(', ')

    if not expression_values:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No fields to update'})
        }

    # Ejecutar la actualización, incluyendo ExpressionAttributeNames solo si es necesario
    update_params = {
        'Key': {'cinema_id': cinema_id, 'show_id': show_id},
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': expression_values
    }
    if expression_names:  # Solo incluir si hay alias definidos
        update_params['ExpressionAttributeNames'] = expression_names

    t_funciones.update_item(**update_params)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Showtime updated successfully'})
    }