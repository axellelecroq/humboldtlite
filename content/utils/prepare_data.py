import json
import csv 
import geocoder



def writeJSON(file, data):
    """
    Store JSON data in a JSON file 
    :param file: str
    :param data: dict
    """
    with open(file, mode='w') as f:
        json.dump(data, f)


def getJSON(path):
    """
    Get data from a JSON file 
    :param path: str
    :return: data
    :rtype: dict
    """
    with open(path, encoding="iso-8859-15" ) as data_file:
       data = json.load(data_file)
    return data;


def avoidTupleInList(data : list):
    """
    Remove the tuple of a list 
    :param data: list
    :return: clean_data
    :rtype: list
    """
    clean_data = []
    for i in data :
        if type(i) != list:
            clean_data.append(i)
    return clean_data


def getYears(dates :list):
    """
    Give all the years of a list of dates
    :param dates: list
    :return: results
    :rtype: list
    """
    results = []
    for i in dates:
        results.append(i[:4])
    return results


def getHumboldtYears(dates:list):
    """
    Give only years of Humboldt's life
    :param dates: list
    :return: results
    :rtype: list
    """
    results = []
    for i in dates:
        try:
            if int(i) > 1769  and int(i) < 1859 :
                results.append(i)
        except: pass
    return results


def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
      
    #read csv file
    with open(csvFilePath, encoding='utf-8') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
          
#csv_to_json('data/databern.csv', 'data/bern.json')


def getGeolocalisationPlace(place):
    """
    Give the geolocation of a giving place.
    The geolocalisation is search in differents local files :
    - location register of edition humboldt
    - location register from GeoName
    If the place isn't already stored in one of this file, then
    a request is sent to the GeoName API.
    :param place: str
    :return: coverage_location
    :rtype: dict
    """
    ortsregister = getJSON('data/edh_ortsregister.json')
    or_geoname = getJSON('data/geoname_ortsregister.json')
    
    coverage_location = {}
    from_geoname = {}
    try :
        for o in ortsregister:
            # If the place of the ortsregister of the edh is the same of the giving place
            # then add the diverse propreties of ortsregister's place to the dict
            # coverage_location
            if place == o['properties']['ContentHeader'] :
                coverage_location["key"] = o['properties']['key']
                coverage_location['geoname_id'] = o['properties']['geoname_id']
                coverage_location['address'] = o['properties']['ContentHeader']
                coverage_location['coordinates'] = o['geometry']['coordinates']
    
        # If the is no place in the ortsregister equal of the giving place
        # then the coverage_location dict stayed empty and we check if the place
        # already was stored in the geoname_ortsregister
        if bool(coverage_location)== False :
            for o in or_geoname:
                for i in o:
                    if place == o[i]["address"]:
                        try:
                            coverage_location["key"] = o[i]['key']
                        except: pass
                        coverage_location['geoname_id'] = o[i]['geoname_id']
                        coverage_location['address'] = i
                        coverage_location['coordinates'] = o[i]['coordinates']

        # If the giving place is neither in the ortsregister of the edh and in
        # stored places from geoname file, then we send a request to geoname to
        # get a geolocation      
        if bool(coverage_location)== False :
            location = geocoder.geonames(place, key='dumont', featureClass='P')
            coverage_location['geoname_id'] = str(location.geonames_id)
            coverage_location['address'] = location.address
            coverage_location['coordinates'] = [location.lng, location.lat]
        
            for ort in ortsregister:
                if ort['properties']['geoname_id'] == str(coverage_location['geoname_id']):
                    coverage_location['key'] = ort['properties']['key']
            from_geoname[place] = coverage_location
        
        # If some geolocalisation from geoname weren't already 
        # stored in some local file, then they are added in the
        # proper geoname_ortsregister.json
        if bool(from_geoname) == True:
            d = getJSON("data/geoname_ortsregister.json")
            d.append(from_geoname)            
            writeJSON("data/geoname_ortsregister.json", d)
    except :
        print(place)
    
    return coverage_location


def bernData():
    dataWithGeo= []
    index = 0
    data = getJSON('data/bern.json')

    for i in data:
        item = {}
        item['link'] = data[index]['ï»¿Link'].split('(')[1].split(')')[0]
        item['title'] = data[index]['ï»¿Link'].split('[')[1].split(']')[0] # ï»¿Link

        if ',' in data[index]['Erscheinungsort']:
            place = data[index]['Erscheinungsort'].split(',')[0]
        elif ';' in data[index]['Erscheinungsort']:
            place = data[index]['Erscheinungsort'].split(';')[0]
        else : place = data[index]['Erscheinungsort']
        item['pubplace'] = getGeolocalisationPlace(place)
        item['year'] = data [index]['Jahr']
        item['language'] = data[index]['Sprache']
        index += 1
        dataWithGeo.append(item)

    writeJSON('data/bern_withgeo.json', dataWithGeo)