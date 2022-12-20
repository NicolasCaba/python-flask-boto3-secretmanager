from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, InvalidRegionError, ParamValidationError
import json
from json.decoder import JSONDecodeError


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/get-secret', methods=['GET'])
def get_secret():
    args = request.args
    secret_name = args.get('secretName')
    region_name = args.get('regionName')

    response = {}
    if secret_name == None and region_name == None:
        response = {"Error": "Ingrese los parametros \"secretName\" y \"regionName\""}
    elif secret_name is None:
        response = {"Error": "Ingrese el parametro \"secretName\""}
    elif region_name is None:
        response = {"Error": "Ingrese el parametro \"regionName\""}
    else:

        try:
            session = boto3.Session(profile_name='work-account')
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )

        
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )

        except ClientError as error:
            response = {"Error": "ClientError", "Code": error.response['Error']['Code'], "FullError": error.response}
        except EndpointConnectionError as error:
            response = {"Error": "EndpointConnectionError", "Message": "Revise la region que introdujo", "FullError": error.args}
        except InvalidRegionError as error:
            response = {"Error": "InvalidRegionError", "Message": "Por favor ingrese una region de aws valida", "FullError": error.args}
        except ParamValidationError as error:
            response = {"Error": "ParamValidationError", "Message": "Por favor revise que los parametros ingresados sean correctos", "FullError": error.args}
        else:
            if 'SecretString' in get_secret_value_response:
                text_secret_data = get_secret_value_response['SecretString']
                try:
                    response = {"secret-name": secret_name, "secret-value": json.loads(text_secret_data)}
                except JSONDecodeError as error:
                    response = {"secret-name": secret_name, "secret-value": text_secret_data}
            else:
                binary_secret_data = get_secret_value_response['SecretBinary']
                response = {"secret-name": secret_name, "secret-value": binary_secret_data}
            
    return jsonify(response)


if __name__=='__main__':
    app.run(debug=True)