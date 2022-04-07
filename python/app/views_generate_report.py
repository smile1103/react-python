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

import csv
from datetime import date
from lxml import etree as ET
import xml.dom.minidom

import pyxml2pdf


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


def get_customerData(customer_file):
    fieldnames = ("ReferenceId",	"CustomerName",	"AnimalNameOrID",	"Species",	"Breed", "LabRefId",	"CollectedDate", "CollectedTime",	"ReceivedDate",	"SampleType",	"SampleVol",
                  "Age", "Sex",	"Height",	"Weight",	"KnownHealthConditions",	"MotherBreed",	"FatherBreed",	"RefVet",	"RefClinic",	"RefClinicAddress",	"OwnerName",	"OwnerEmail",	"OwnerAddress")
    customer_reader = csv.DictReader(customer_file, fieldnames)
    customer_data = {}
    for each in customer_reader:
        if each['LabRefId'] != 'LabRefId':
            row = {}
            row['LabRefId'] = each['LabRefId']
            row['ReferenceId'] = each['ReferenceId']
            row['CustomerName'] = each['CustomerName']
            row['AnimalNameOrID'] = each['AnimalNameOrID']
            row['Species'] = each['Species']
            row['Breed'] = each['Breed']
            row['CollectedDate'] = each['CollectedDate']
            row['CollectedTime'] = each['CollectedTime']
            row['ReceivedDate'] = each['ReceivedDate']
            row['SampleType'] = each['SampleType']
            row['SampleVol'] = each['SampleVol']
            row['Age'] = each['Age']
            row['Sex'] = each['Sex']
            row['Height'] = each['Height']
            row['Weight'] = each['Weight']
            row['KnownHealthConditions'] = each['KnownHealthConditions']
            row['MotherBreed'] = each['MotherBreed']
            row['FatherBreed'] = each['FatherBreed']
            row['RefVet'] = each['RefVet']
            row['RefClinic'] = each['RefClinic']
            row['RefClinicAddress'] = each['RefClinicAddress']
            row['OwnerName'] = each['OwnerName']
            row['OwnerEmail'] = each['OwnerEmail']
            row['OwnerAddress'] = each['OwnerAddress']
            customer_data[each['LabRefId']] = row
    return customer_data


def get_result(obj, value):
    for k, v in obj.items():
        if value in v:
            return k


def analyze_column(col, analysis, gender):
    lst = {'M': [], 'F': []}
    for marker, value in col.items():
        obj = analysis.get(marker)
        if obj is None:
            continue
        obj_class = obj['class']
        obj_inheritance = obj['inheritancePattern']
        obj_type = obj['type']
        m_data = get_gender(obj['analysisGender'], 'M')
        m_result = get_result(m_data, value)
        m_result_obj = {
            'markerId': marker,
            'class': obj_class,
            'inheritancePattern': obj_inheritance,
            'type': obj_type,
            'genotype': value,
            'result': m_result
        }
        lst['M'].append(m_result_obj)
        f_data = get_gender(obj['analysisGender'], 'F')
        f_result = get_result(f_data, value)
        f_result_obj = {
            'markerId': marker,
            'class': obj_class,
            'inheritancePattern': obj_inheritance,
            'type': obj_type,
            'genotype': value,
            'result': f_result
        }
        lst['F'].append(m_result_obj)
    return lst


def filterMarkerResult(arr):
    markerIds = []
    for obj in arr:
        if obj['result'] == 'positiveGenotype':
            markerIds.append(obj['markerId'])
    return markerIds


def getMarkerList(arr, ids):
    markerList = []
    for obj in arr:
        for id in ids:
            if id == obj['markerName']:
                markerList.append(obj)
    return markerList


def createXML(data, canineFile):
    with open(canineFile, "r") as json_Canine:
        Data = json.load(json_Canine)
    markerResultIds = filterMarkerResult(data['markerResults'])
    markerList = getMarkerList(Data['markerList'], markerResultIds)
    root = ET.Element("DocumentElement")

    # First Sub Element
    CoverPage = ET.SubElement(root, "CoverPage")
    CoverPageImagePath = ET.SubElement(CoverPage, "CoverPageImagePath")

    AnimalName = ET.SubElement(CoverPage, "AnimalName")
    AnimalName.text = data['customer_data']['AnimalNameOrID']

    TestName = ET.SubElement(CoverPage, "TestName")
    TestName.text = Data['projectName']

    TotalMarkers = ET.SubElement(CoverPage, "TotalMarkers")
    TotalMarkers.text = Data['totalMarkers']

    ProjectStatus = ET.SubElement(CoverPage, "ProjectStatus")
    ProjectStatus.text = Data['projectStatus']

    MarkerType = ET.SubElement(CoverPage, "MarkerType")

    SNP = ET.SubElement(MarkerType, "SNP")
    SNP.text = Data['markerTypeData']['snp']

    INS = ET.SubElement(MarkerType, "INS")
    INS.text = Data['markerTypeData']['ins']

    DEL = ET.SubElement(MarkerType, "DEL")
    DEL.text = Data['markerTypeData']['del']

    MNP = ET.SubElement(MarkerType, "MNP")
    MNP.text = Data['markerTypeData']['mnp']

    CNV = ET.SubElement(MarkerType, "CNV")
    CNV.text = Data['markerTypeData']['cnv']

    ConditionType = ET.SubElement(CoverPage, "ConditionType")

    # Twele Sub Element
    TableOfContents = ET.SubElement(root, "TableOfContents")

    IllustrationImagePath = ET.SubElement(
        TableOfContents, "IllustrationImagePath")
    TitleImagePath = ET.SubElement(TableOfContents, "TitleImagePath")
    Title = ET.SubElement(TableOfContents, "Title")

    TableOfContentsList = ET.SubElement(TableOfContents, "TableOfContentsList")

    for dataMap in Data['TableOfContentListItem']:
        TableOfContentsListItem = ET.SubElement(
            TableOfContentsList, "TableOfContentsListItem")
        TableOfContentsListItem.attrib["ID"] = dataMap['ID']

        Heading = ET.SubElement(TableOfContentsListItem, "Heading")
        HeadingName = ET.SubElement(Heading, "HeadingName")
        HeadingName.text = dataMap['HeadingName']

        PageNumber = ET.SubElement(Heading, "PageNumber")
        PageNumber.text = dataMap['PageNumber']

        SubHeadingList = ET.SubElement(
            TableOfContentsListItem, "SubHeadingList")
        SubHeadingListItem = ET.SubElement(
            SubHeadingList, "SubHeadingListItem")
        SubHeadingListItem.attrib["ID"] = dataMap['ID']

        SubHeadingName = ET.SubElement(SubHeadingList, "SubHeadingName")
        SubHeadingName.text = dataMap['SubHeadingName']

    Disorder = ET.SubElement(ConditionType, "Disorder")
    Disorder.text = Data['conditionTypeData']['disorder']

    Trait = ET.SubElement(ConditionType, "Trait")
    Trait.text = Data['conditionTypeData']['trait']

    MarkerList = ET.SubElement(CoverPage, "MarkerList")

    for marker in markerList:
        MarkerName = ET.SubElement(MarkerList, "MarkerName")
        MarkerName.text = marker['markerName']

        CurrentStatus = ET.SubElement(MarkerList, "CurrentStatus")
        CurrentStatus.text = marker['currentStatus']

        FieldList = ET.SubElement(MarkerList, "FieldList")

        for obj in marker['fieldList']:
            List = ET.SubElement(FieldList, "List")

            FieldName = ET.SubElement(List, "FieldName")
            FieldName.text = obj['fieldName']

            Value = ET.SubElement(List, "Value")
            Value.text = obj['value']

        ArticleList = ET.SubElement(MarkerList, "ArticleList")

        for obj in marker['articalList']:
            List = ET.SubElement(ArticleList, "List")

            Authors = ET.SubElement(List, "Authors")
            Authors.text = obj['authors']

            Title = ET.SubElement(List, "Title")
            Title.text = obj['title']

            Journal = ET.SubElement(List, "Journal")
            Journal.text = obj['journal']

    # Second Sub Element
    ReportHeader = ET.SubElement(root, "ReportHeader")
    LogoImagePath = ET.SubElement(ReportHeader, "LogoImagePath")

    # Third Sub Element
    ReportFooter = ET.SubElement(root, "ReportFooter")
    Name = ET.SubElement(ReportFooter, "Name")
    Name.text = data['customer_data']['AnimalNameOrID']

    AgeSex = ET.SubElement(ReportFooter, "AgeSex")
    AgeSex.text = data['customer_data']['Age']

    SampleID = ET.SubElement(ReportFooter, "SampleID")
    SampleID.text = data["sampleId"]

    SampleType = ET.SubElement(ReportFooter, "SampleType")
    SampleType.text = data['customer_data']['SampleType']

    SwabKit = ET.SubElement(ReportFooter, "SwabKit")
    ReportDate = ET.SubElement(ReportFooter, "ReportDate")
    ReportDate.text = data["reportDate"]

    PageNumber = ET.SubElement(ReportFooter, "PageNumber")

    # Fourth Sub Element
    LogoImagePath = ET.SubElement(root, "LogoImagePath")

    # Fifth Sub Element
    IllustrationImagePath = ET.SubElement(root, "IllustrationImagePath")

    # Six Sub Element
    Title = ET.SubElement(root, "Title")

    # Seven Sub Element
    AnimalName = ET.SubElement(root, "AnimalName")
    AnimalName.text = data['customer_data']['AnimalNameOrID']

    # Eight Sub Element
    BasicDetails = ET.SubElement(root, "BasicDetails")

    Breed = ET.SubElement(BasicDetails, "Breed")
    Breed.text = data['customer_data']['Breed']

    Sex = ET.SubElement(BasicDetails, "Sex")
    Sex.text = data['customer_data']['Sex']

    Age = ET.SubElement(BasicDetails, "Age")
    Age.text = data['customer_data']['Age']

    ParentBreedMother = ET.SubElement(BasicDetails, "ParentBreedMother")
    ParentBreedMother.text = data['customer_data']['MotherBreed']

    ParentBreedFather = ET.SubElement(BasicDetails, "ParentBreedFather")
    ParentBreedFather.text = data['customer_data']['FatherBreed']

    Weight = ET.SubElement(BasicDetails, "Weight")
    Weight.text = data['customer_data']['Weight']

    Height = ET.SubElement(BasicDetails, "Height")
    Height.text = data['customer_data']['Height']

    KnownHealthConditions = ET.SubElement(
        BasicDetails, "KnownHealthConditions")
    KnownHealthConditions.text = data['customer_data']['KnownHealthConditions']

    # Nine Sub Element
    SampleDetails = ET.SubElement(root, "SampleDetails")

    ReferenceID = ET.SubElement(SampleDetails, "ReferenceID")
    ReferenceID.text = data['customer_data']['ReferenceId']

    CollectedDate = ET.SubElement(SampleDetails, "CollectedDate")
    CollectedDate.text = data['customer_data']['CollectedDate']

    SampleType = ET.SubElement(SampleDetails, "SampleType")
    SampleType.text = data['customer_data']['SampleType']

    LabReferenceID = ET.SubElement(SampleDetails, "LabReferenceID")
    LabReferenceID.text = data['customer_data']['LabRefId']

    ReceivedDate = ET.SubElement(SampleDetails, "ReceivedDate")
    ReceivedDate.text = data['customer_data']['ReceivedDate']

    ReportedDate = ET.SubElement(SampleDetails, "ReportedDate")
    ReportedDate.text = data['reportDate']

    # Ten Sub Element
    ReferenceDetails = ET.SubElement(root, "ReferenceDetails")

    ReferenceID = ET.SubElement(ReferenceDetails, "ReferenceID")
    ReferenceID.text = data['customer_data']['ReferenceId']

    ClinicName = ET.SubElement(ReferenceDetails, "ClinicName")
    ClinicName.text = data['customer_data']['RefClinic']

    ClinicAddress = ET.SubElement(ReferenceDetails, "ClinicAddress")
    ClinicAddress.text = data['customer_data']['RefClinicAddress']

    OwnerName = ET.SubElement(ReferenceDetails, "OwnerName")
    OwnerName.text = data['customer_data']['OwnerName']

    EmailAddress = ET.SubElement(ReferenceDetails, "EmailAddress")
    EmailAddress.text = data['customer_data']['OwnerEmail']

    OwnerAddress = ET.SubElement(ReferenceDetails, "OwnerAddress")
    OwnerAddress.text = data['customer_data']['OwnerAddress']

    GenomicTestDetails = ET.SubElement(root, "GenomicTestDetails")

    Panel = ET.SubElement(GenomicTestDetails, "Panel")
    Panel.text = Data['genomicTestDetails']['panel']

    Laboratory = ET.SubElement(GenomicTestDetails, "Laboratory")
    Laboratory.text = Data['genomicTestDetails']['laboratory']

    Technology = ET.SubElement(GenomicTestDetails, "Technology")
    Technology.text = Data['genomicTestDetails']['technology']

    Machine = ET.SubElement(GenomicTestDetails, "Machine")
    Machine.text = Data['genomicTestDetails']['machine']

    LibPrepSolution = ET.SubElement(GenomicTestDetails, "LibPrepSolution")
    LibPrepSolution.text = Data['genomicTestDetails']['libPrepSolution']

    PanelSize = ET.SubElement(GenomicTestDetails, "PanelSize")
    PanelSize.text = Data['genomicTestDetails']['panelSize']

    MarkerCoverage = ET.SubElement(GenomicTestDetails, "MarkerCoverage")
    MarkerCoverage.text = Data['genomicTestDetails']['markerCoverage']

    ResultSummaryPage = ET.SubElement(root, "ResultSummaryPage")
    TitleImagePath = ET.SubElement(ResultSummaryPage, "TitleImagePath")
    Title = ET.SubElement(ResultSummaryPage, "Title")

    Disorders = ET.SubElement(ResultSummaryPage, "Disorders")

    DisorderCount = ET.SubElement(Disorders, "DisorderCount")
    DisorderList = ET.SubElement(Disorders, "DisorderList")
    DisorderListItem = ET.SubElement(DisorderList, "DisorderListItem")
    DisorderListItem.attrib["ID"] = Data["ResultSummaryPage"]["Disorders"]["ID"]

    DisorderName = ET.SubElement(DisorderListItem, "DisorderName")
    DisorderName.text = Data["ResultSummaryPage"]["Disorders"]['DisorderName']

    Type = ET.SubElement(DisorderListItem, "Type")
    Type.text = Data["ResultSummaryPage"]["Disorders"]['Type']

    Marker = ET.SubElement(DisorderListItem, "Marker")
    Marker.text = Data["ResultSummaryPage"]["Disorders"]['Marker']

    Gene = ET.SubElement(DisorderListItem, "Gene")
    Gene.text = Data["ResultSummaryPage"]["Disorders"]['Gene']

    Inheritance = ET.SubElement(DisorderListItem, "Inheritance")
    Inheritance.text = Data["ResultSummaryPage"]["Disorders"]['Inheritance']

    Summary = ET.SubElement(DisorderListItem, "Summary")
    Summary.text = Data["ResultSummaryPage"]["Disorders"]['Summary']

    Carriers = ET.SubElement(ResultSummaryPage, "Carriers")

    CarrierCount = ET.SubElement(Carriers, "CarrierCount")
    CarrierList = ET.SubElement(Carriers, "CarrierList")

    for dataMap in Data["ResultSummaryPage"]['Carriers']:
        CarrierListItem = ET.SubElement(CarrierList, "CarrierListItem")
        CarrierListItem.attrib["ID"] = dataMap['ID']

        CarrierName = ET.SubElement(CarrierListItem, "CarrierName")
        CarrierName.text = dataMap['CarrierName']

        Type = ET.SubElement(CarrierListItem, "Type")
        Type.text = dataMap['Type']

        Marker = ET.SubElement(CarrierListItem, "Marker")
        Marker.text = dataMap['Marker']

        Gene = ET.SubElement(CarrierListItem, "Gene")
        Gene.text = dataMap['Gene']

        Inheritance = ET.SubElement(CarrierListItem, "Inheritance")
        Inheritance.text = dataMap['Inheritance']

        Summary = ET.SubElement(CarrierListItem, "Summary")
        Summary.text = dataMap['Summary']

    Traits = ET.SubElement(root, "Traits")
    TraitCount = ET.SubElement(Traits, "TraitCount")
    TraitList = ET.SubElement(Traits, "TraitList")
    TraitListItem = ET.SubElement(TraitList, "TraitListItem")
    TraitListItem.attrib["ID"] = Data["ResultSummaryPage"]["Traits"]['ID']

    TraitName = ET.SubElement(TraitListItem, "TraitName")
    TraitName.text = Data["ResultSummaryPage"]["Traits"]['TraitName']

    Marker = ET.SubElement(TraitListItem, "Marker")
    Marker.text = Data["ResultSummaryPage"]["Traits"]['Marker']

    Gene = ET.SubElement(TraitListItem, "Gene")
    Gene.text = Data["ResultSummaryPage"]["Traits"]['Gene']

    Inheritance = ET.SubElement(TraitListItem, "Inheritance")
    Inheritance.text = Data["ResultSummaryPage"]["Traits"]['Inheritance']

    Summary = ET.SubElement(TraitListItem, "Summary")
    Summary.text = Data["ResultSummaryPage"]["Traits"]['Summary']
# Ten Sub Element
    MarkerResults = ET.SubElement(root, "MarkerResults")
    for obj in data['markerResults']:

        MarkerResult = ET.SubElement(MarkerResults, "MarkerResult")

        MarkerId = ET.SubElement(MarkerResult, "MarkerId")
        MarkerId.text = obj['markerId']

        Class = ET.SubElement(MarkerResult, "Class")
        Class.text = obj['class']

        InheritancePattern = ET.SubElement(MarkerResult, "InheritancePattern")
        InheritancePattern.text = obj['inheritancePattern']

        Type = ET.SubElement(MarkerResult, "Type")
        Type.text = obj['type']

        Genotype = ET.SubElement(MarkerResult, "GenoType")
        Genotype.text = obj['genotype']

        Result = ET.SubElement(MarkerResult, "Result")
        Result.text = obj['result']

    filename = data["sampleId"]+"output.xml"

    tree = ET.ElementTree(root)
    tree.write(filename)

    dom = xml.dom.minidom.parse(filename)
    final_output = dom.toprettyxml()
    # listdir.remove(filename)

    with open(filename, "w") as xml_file:
        xml_file.write(final_output)


def main(matrix_filename, analysis_filename, output_filename, customer_filename, id=None, gender='M'):
    df = pd.read_csv(matrix_filename, sep='\t', index_col=0)
    analysis_file = open(analysis_filename, 'r', encoding='utf-8')
    analysis_arr = json.load(analysis_file)['markerList']
    customer_file = open(customer_filename, 'r')
    customer_data = get_customerData(customer_file)
    analysis = create_analsis_dict(analysis_arr)
    analysis_file.close()
    for name, col in df.iteritems():
        sample_id, barcode = name.strip().split(';')
        if id is None or sample_id == id:
            results = analyze_column(col, analysis, gender)
            today = date.today()
            customerGender = customer_data[sample_id]['Sex']
            markerResult = []
            if customerGender == 'Male' or customerGender == "M":
                markerResult = results['M']
            else:
                markerResult = results['F']
            sampleCustomer = {
                'barcode': barcode,
                'sampleId': sample_id,
                'reportDate': today.strftime("%d/%m/%Y"),
                'customer_data': customer_data[sample_id],
                'markerResults': markerResult
            }
            createXML(sampleCustomer,
                      "app/CanineTDv1c2-Published-FullContent-03132022210100.json")
            with open("app/"+sample_id+output_filename, 'w', encoding='utf-8') as sam:
                json.dump(sampleCustomer, sam, indent=4)


class generate_report(APIView):
    def post(self, request):
        input_file = None
        request_data = QueryDict('', mutable=True)
        request_data.update(request.data)
        file_number = int(request_data['filenumber'])

        if (file_number == 1):
            input_file = "Canine_Genotype matrix file_run07012022-2.xls"
        else:
            input_file = "app/693-R_2021_01_15_09_35_30_user_S5XL-0237-63-Genomia-Pilsen-canine-PITD-Matrix.xls"

        if input_file is None:
            print('Did not fine an xls file in the directory, exiting')
        else:
            res = main('app/'+input_file, 'app/markeranalysis.json',
                       'markerresults.json', 'app/SampleCustomerData-022222-01.csv', None)

        return Response(res)


class generate_specific_report(APIView):
    def post(self, request):
        input_file = None
        request_data = QueryDict('', mutable=True)
        request_data.update(request.data)
        file_number = int(request_data['filenumber'])
        sample_id = request_data['sampleID']

        if (file_number == 1):
            input_file = "Canine_Genotype matrix file_run07012022-2.xls"
        else:
            input_file = "app/693-R_2021_01_15_09_35_30_user_S5XL-0237-63-Genomia-Pilsen-canine-PITD-Matrix.xls"

        if input_file is None:
            print('Did not fine an xls file in the directory, exiting')
        else:
            res = main('app/'+input_file, 'app/markeranalysis.json',
                       'markerresults.json', 'app/SampleCustomerData-022222-01.csv', sample_id)

        return Response(res)
