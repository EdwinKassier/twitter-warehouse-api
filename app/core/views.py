
from flask import Blueprint, current_app,request
from werkzeug.local import LocalProxy
import json

from authentication import check_auth

import os
from google.cloud import bigquery

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../../credentials.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\twitter-warehouse-api\credentials.json"

client = bigquery.Client()


from .tasks import test_task

core = Blueprint('core', __name__)
logger = LocalProxy(lambda: current_app.logger)


@core.before_request
def before_request_func():
    current_app.logger.name = 'core'

#Preparing for prod release cloud run, test
@core.route('/process_request', methods=['GET'])
def test():
    logger.info('app test route hit')
    try:


        
        sql = """
                SELECT DISTINCT Name
                FROM (SELECT * FROM `edwin-portfolio-358212.twitter_output_data_warehouse.twitter_cleaned_data`ORDER BY Volume DESC)
            """

        df = client.query(sql).to_dataframe()


        df = df.assign(id=range(len(df)))

        df = df.assign(id = lambda x: df['id']+ 1)

        output = df.to_dict('records')

        print(output)

        return json.dumps({"data":output}), 200, {"ContentType": "application/json"}
    except Exception as e:
        print(e)
        return json.dumps({"message": e}), 500, {"ContentType": "application/json"}



@core.route('/restricted', methods=['GET'])
@check_auth
def restricted():
    return json.dumps({"message": 'Successful Auth'}), 200, {"ContentType": "application/json"}
