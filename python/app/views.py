from rest_framework.decorators import APIView

import pandas as pd
import json
from os import listdir

from django.http import QueryDict
from django.core import serializers

from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser

from .models import *
from .serializers import CustomerFileSerializer

def create_analsis_dict(analysis_arr):
    d = {}
    for obj in analysis_arr:
        marker = obj['markerId']
        del obj['markerId']
        d[marker] = obj
    return d


def get_gender(obj, gender):
    for gender_obj in obj:
        if gender_obj.get('gender') == gender:
            return gender_obj


def get_result(obj, value):
    for k, v in obj.items():
        if value in v:
            return k


def analyze_column(col, analysis, gender):
    lst = []
    for marker, value in col.items():
        obj = analysis.get(marker)
        if obj is None:
            continue
        obj_class = obj['class']
        obj_inheritance = obj['inheritancePattern']
        obj_type = obj['type']
        data = get_gender(obj['analysisGender'], gender)
        result = get_result(data, value)
        result_obj = {
            'markerId': marker,
            'class': obj_class,
            'inheritancePattern': obj_inheritance,
            'type': obj_type,
            'genotype': value,
            'result': result
        }
        lst.append(result_obj)
    return lst


def main(matrix_filename, analysis_filename, gender='M'):
    df = pd.read_csv(matrix_filename, sep='\t', index_col=0)
    analysis_file = open(analysis_filename, 'r', encoding='utf-8')
    analysis_arr = json.load(analysis_file)['markerList']
    analysis = create_analsis_dict(analysis_arr)
    analysis_file.close()
    sample_list = []
    for name, col in df.iteritems():
        sample_id, barcode = name.strip().split(';')
        results = analyze_column(col, analysis, gender)
        obj = {
            'barcode': barcode,
            'sampleId': sample_id,
            'animalSpecies': '',
            'animalBreed': '',
            'reportDate': '',
            'customerData': {
                "animalName": '',
                "ownerName": '',
                "vetName": '',
                "clinicName": '',
                "customerName": '',
                "referenceId": '',
                "referenceDate": ''
            },
            'markerResults': results
        }
        sample_list.append(obj)
    final_obj= {
        'sampleList': sample_list
    }
    
    return json.dumps(final_obj)



class json_data(APIView):
    def get(self, request):
        input_file = None
        for file in listdir("app"):
            if file.endswith('xls'):
                # print(file)

                if (file == "Canine_Genotype matrix file_run07012022-2.xls"):
                    input_file = file
                else:
                    input_file = "693-R_2021_01_15_09_35_30_user_S5XL-0237-63-Genomia-Pilsen-canine-PITD-Matrix.xls"
                break
        if input_file is None:
            print('Did not fine an xls file in the directory, exiting')
        else:
            res = main('app/'+input_file, 'app/analysis.json')

        return Response(res)

    def post(self, request):
        input_file = None
        request_data = QueryDict('', mutable=True)
        request_data.update(request.data)
        file_number = int(request_data['file_number'])

        # print(file_number)

        if (file_number == 1):
            input_file = "Canine_Genotype matrix file_run07012022-2.xls"
        else:
            input_file = "693-R_2021_01_15_09_35_30_user_S5XL-0237-63-Genomia-Pilsen-canine-PITD-Matrix.xls"
        
        if input_file is None:
            print('Did not fine an xls file in the directory, exiting')
        else:
            res = main('app/'+input_file, 'app/analysis.json')
        
        return Response(res)

    # View For Posting XLS file from client side
    # def post(self, request):
    #     input_file = request.FILES['file']
    #     path = default_storage.save(input_file.name, ContentFile(input_file.read()))

    #     if input_file is None:
    #         print('Did not fine an xls file in the directory, exiting')
    #     else:
    #         res = main(path, f'app/analysis.json')

    #     return Response(res)

class customer_data(APIView):
    parser_classes = (JSONParser, MultiPartParser, FileUploadParser, FormParser, )

    def get(self, request):
        last_three = CustomerFile.objects.all().order_by('-id')[:3]

        serialized_q = serializers.serialize('json',
                                      list(last_three),
                                      fields=('date_created','customer_file','note'))

        return Response(serialized_q)

    def post(self, request):
        request_data = QueryDict('', mutable=True)
        request_data.update(request.data)
        file_name = request_data['customer_file'].name

        if (file_name.split(".")[1] == "csv"):
            data = CustomerFile.objects.create(note=request_data['note'], customer_file=request_data['customer_file'])
            
            if data is not None:
                data.save()
                return Response("Customer File Uploaded")
            else:
                return Response("Error Submiting Data")

        else:
            return Response(".csv file required")
        
