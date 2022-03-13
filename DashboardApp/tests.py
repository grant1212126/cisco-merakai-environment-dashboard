from django.contrib.auth.forms import UserModel
from django.test import TestCase
from DashboardApp.models import WeatherOptions, Location, Sensor, DataPoint

# Tests the applications models on vaiours aspects

class ModelTests(TestCase):

    # Creates temporary databse entries to test against in unit tests

    def setUp(self):

        Location.objects.create(name = "Glasgow", description = "Scotland, United Kingdom")

        Sensor.objects.create(org_id = 1, serial = 1, kind = "Camera", location = Location.objects.get(name="Glasgow"), description = "description", interval = 10)

        Sensor.objects.create(org_id = 1, serial = 2, kind = "Environmental", location = Location.objects.get(name="Glasgow"), description = "description", interval = 10)

        Sensor.objects.create(org_id = 1, serial = 3, kind = "Environmental", location = Location.objects.get(name="Glasgow"), description = "description", interval = 10)

        DataPoint.objects.create(kind = "Temperature", location = Location.objects.get(name="Glasgow"), sensor = Sensor.objects.get(org_id=1, serial=2), value = 20.04)

        DataPoint.objects.create(kind = "Humidity", location = Location.objects.get(name="Glasgow"), sensor = Sensor.objects.get(org_id=1, serial=3), value = 410)

        DataPoint.objects.create(kind = "Occupancy", location = Location.objects.get(name="Glasgow"), sensor = Sensor.objects.get(org_id=1, serial=1), value = 5)

    # Tests if each locatiion object has a name (name is the unique idendifier)

    def test_Location(self):

        for l in Location.objects.all():
            
            self.assertTrue(l.name != None, "Error, Location instance exists with no name, please check location: " + str(l.id))

    # Tests the all the sensor objects to make sure each constraint is satisfied 

    def test_Sensor(self):

        for s in Sensor.objects.all():

            self.assertTrue(s.org_id != None, "Error, Sensor instance exists with no org_id, please check Sensor: " + str(s.org_id) + str(s.serial))

            self.assertTrue(s.serial != None, "Error, Sensor instance exists with no serial, please check Sensor: " + str(s.org_id) + str(s.serial))
            
            self.assertTrue(s.location != None, "Error, Sensor instance exists with no location, please check Sensor: " + str(s.org_id) + str(s.serial))

            self.assertTrue(s.location != None, "Error, Sensor instance exists with no kind value, please check Sensor: " + str(s.org_id) + str(s.serial))

            self.assertTrue(s.kind in Sensor.Kind, "Error, Sensor instance exists with incorrect kind not in Sensor.Kind list, please check Sensor: " + str(s.org_id) + str(s.serial))

    # Tests all the DataPoint objects to make sure each constraint is satisfied

    def test_DataPoint(self):

        for d in DataPoint.objects.all():

            self.assertTrue(d.location != None, "Error, DataPoint instance exists with no location, please check DataPoint: " + str(d.id))

            self.assertTrue(d.sensor != None, "Error, DataPoint instance exists with no sensor, please check DataPoint: " + str(d.id))

            self.assertTrue(d.kind in DataPoint.Kind, "Error, DataPoint instance exists with incorrect kind not in DataPoint.Kind list, please check DataPoint: " + str(d.id))

            self.assertTrue(d.tstamp != None, "Error, DataPoint instance exists with no tstamp value, please check DataPoint: " + str(d.id))

            self.assertTrue(d.value != None, "Error, DataPoint instance exists with no value, please check DataPoint: " + str(d.id))

# Tests the applications views on various aspects

class ViewTests(TestCase):

    # Sets up a user to be used for testing purposes in the views.

    def setUp(self):

        user = UserModel.objects.create(username='testuser', password='12345')

    # Tests if the authentication for the Aplications is functional, tests if application returns
    # the correct responses.

    def test_authentication(self):

        response = self.client.get('/') # Base URL, leads to homepage
        self.assertEqual(response.status_code, 302, "Error, user not correctly redirected to login page")

        self.client.force_login(UserModel.objects.get_or_create(username='testuser')[0]) # User is now logged in, should be able to access dashboard

        response = self.client.get('/') 
        self.assertEqual(response.status_code, 200, "Error, logged in user still cannot access dashboard")

    # Tests if the applications redirect to the correct locations, e.g. return the correct response 

    def test_view_urls_at_correct_area(self):

        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200, "Error, login settings page not at correct area")

        self.client.force_login(UserModel.objects.get_or_create(username='testuser')[0])

        response = self.client.get('/settings/weather/')
        self.assertEqual(response.status_code, 200, "Error, weather settings page not at correct area")

        response = self.client.get('/settings/locations/')
        self.assertEqual(response.status_code, 200, "Error, location settings page not at correct area")

        response = self.client.get('/settings/sensors/')
        self.assertEqual(response.status_code, 200, "Error, sensors settings page not at correct area")

        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302, "Error, logout page does not correctly redirect")

        