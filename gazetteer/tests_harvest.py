from django.test import TestCase
from django.core.urlresolvers import reverse
import datetime
import json
from mapstory.tests import MapStoryTestMixin, AdminClient
from .models import Location,LocationName,GazSource
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT
from gazetteer.harvest import harvest

class GazHarvestTest(TestCase):

    def setUp(self):
        #import pdb; pdb.set_trace()
        # import so there is a GazSource object available to test inserting link back to source config
        import gazetteer.test_geonode_config

        sch = Scheme.objects.create(uri=TARGET_NAMESPACE_FT[:-1], pref_label="Gaz Features types")
       
        ft = Concept.objects.create(term="PPL", pref_label="Populated Place", definition = "def", scheme = sch)
        loc1 = Location.objects.create(defaultName="Wollongong", locationType=ft, latitude=-34.433056 , longitude=150.883057 )
        source= GazSource.objects.first()
        ln1 = LocationName.objects.create(name="Wollongong", language='en', location=loc1 )
        ln1.nameUsed.add(source)
        ln2 = LocationName.objects.create(name="http://dbpedia.org/resource/Wollongong", language='', namespace="http://dbpedia.org/resource/", location=loc1 )
        ln2.nameUsed.add(source)
        # now set up cross references from another namespace
        sch2 = Scheme.objects.create(uri="http://mapstory.org/def/ft/nga", pref_label="NGA gaz codes")
        ft2 = Concept.objects.create(term="PPLA", pref_label="Populated Place", definition = "def", scheme = sch2)
        mr = MapRelation.objects.create(match_type=  1, origin_concept=ft2 , uri="".join((TARGET_NAMESPACE_FT,"PPL")))
       
    def test_location_match(self):
        """
        Tests finding a gazetteer entry.
        """
        #import pdb; pdb.set_trace()
        data = json.loads ( '''{
            "locationType": "PPL",
            "names": [
                {
                "name": "Wollongong",
                "language": "en"
                }
            ]
            }''' )
        
        
        c = AdminClient()
        response = c.post(reverse('matchloc'),  data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, 'Not found: body ' + response.content )
        locr = json.loads(response.content)
        
        # import ipdb; ipdb.set_trace()
        self.assertIsInstance(locr,dict,'Response type not formatted as valid dictionary' )
        self.assertTrue(locr.has_key('name_lang'),'Response does not include name+language match list' )
        self.assertEqual(len(locr['name_lang']), 1, 'Response should contain exactly one match : ' + response.content) 
        self.assertEqual(locr['name_lang'][0]['defaultName'], "Wollongong")       
      
        data = json.loads ( '''{
            "locationType": "PPL",
            "names": [
                {
                "name": "http://dbpedia.org/resource/Wollongong",
                "namespace": "http://dbpedia.org/resource/"
                }
            ]
            }''' )
        
        
        c = AdminClient()
        response = c.post(reverse('matchloc'),  data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, 'Error matching: body ' + response.content)
        locr = json.loads(response.content)
        self.assertEqual(len(locr['name_lang']), 0, 'Response should not contain name match: ' + response.content)
        self.assertEqual(len(locr['code']), 1, 'Response should contain a code based match: ' + response.content)        
        self.assertEqual(locr['code'][0]['defaultName'], "Wollongong")
        # self.assertEqual(locr['defaultName'], "Wollongong")
        # self.assertEqual(locr['defaultName'], "Wollongong") 
        
        data = json.loads ( '''{
            "locationType": "XXX",
            "names": [
                {
                "name": "Wollongong",
                "language": "en"
                }
            ]
            }''' )

        c = AdminClient()
        response = c.post(reverse('matchloc'),  data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, 'Response should be 200, with empty list')
        locr = json.loads(response.content)
        self.assertEqual(len(locr['code'])+len(locr['name_lang'])+len(locr['name']), 0, 'Response should not contain any matches: ' + response.content)
 
    def test_locationname_insert(self):
        """
        Tests insertion of a name to a specific location .
        """
        import pdb; pdb.set_trace()
        loc= Location.objects.first()
        
        c = AdminClient()
        response = c.get(reverse('getloc', args=[loc.id]))
        self.assertEqual(response.status_code, 200)

        c.login_as_admin()

        data = {"name":"The Gong","language":'en'}

        response = c.post(reverse('recordname', args=[loc.id]), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        locx = Location.objects.get(id=loc.id)

        response = c.get(reverse('getloc', args=[loc.id]))
        
        self.assertEqual(response.status_code, 200)
        locr = json.loads(response.content)
    
        data = {"name":"732","namespace":'http://abs.gov.au/admincodes/',"language":''}
        response = c.post(reverse('recordname', args=[loc.id]), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)    

        response = c.get(reverse('getloc', args=[loc.id]))
        
        self.assertEqual(response.status_code, 200)
        locr = json.loads(response.content)
        
        # now we can test it - it shows up OK in the debugger here..
        
#        self.assertEqual(locr.names, m)
 