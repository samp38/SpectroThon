# 
# Copyright 2012-2013 Jeremy Hall
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# 

import unittest
import stellarnet

class TestStellarNet(unittest.TestCase):

    def setUp(self):
        devices = stellarnet.find_devices()
        self.spectro = devices[0]

    def tearDown(self):
        del self.spectro
        
    def test_int_time(self):
        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(int_time = -1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(int_time = 1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(int_time = 65536);

        self.assertEqual(self.spectro.get_config()['int_time'], 100, 
                         'wrong default')

        self.spectro.set_config(int_time = 500)
        self.assertEqual(self.spectro.get_config()['int_time'], 500,
                         'getter should return set value')

    def test_x_timing(self):
        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(x_timing = -1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(x_timing = 0);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(x_timing = 4);
        
        self.assertEqual(self.spectro.get_config()['x_timing'], 3, 
                         'wrong default')

        self.spectro.set_config(x_timing = 1)
        self.assertEqual(self.spectro.get_config()['x_timing'], 1,
                         'getter should return set value')

    def test_x_smooth(self):
        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(x_smooth = -1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(x_smooth = 5);
        
        self.assertEqual(self.spectro.get_config()['x_smooth'], 0, 
                         'wrong default')

        self.spectro.set_config(x_smooth = 4)
        self.assertEqual(self.spectro.get_config()['x_smooth'], 4,
                         'getter should return set value')

    def test_scans_to_avg(self):
        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(scans_to_avg = -1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(scans_to_avg = 0);
        
        self.assertEqual(self.spectro.get_config()['scans_to_avg'], 1, 
                         'wrong default')

        self.spectro.set_config(scans_to_avg = 10)
        self.assertEqual(self.spectro.get_config()['scans_to_avg'], 10,
                         'getter should return set value')

    def test_temp_comp(self):
        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(temp_comp = -1);

        with self.assertRaises(stellarnet.ArgRangeError):
            self.spectro.set_config(temp_comp = 1);
        
        self.assertEqual(self.spectro.get_config()['temp_comp'], 0, 
                         'wrong default')

        self.spectro.set_config(temp_comp = 0)
        self.assertEqual(self.spectro.get_config()['temp_comp'], 0,
                         'getter should return set value')

    def test_coeffs(self):
        try:
            coeffs = self.spectro.get_config()['coeffs']
        except KeyError:
            self.assertTrue(True, 'old device')
        else:
            self.assertEqual(len(coeffs), 4, 
                             'should have 4 coefficient elements')

    def test_lambda(self):
        self.assertRaises(stellarnet.ArgTypeError, self.spectro.compute_lambda, 1.1)

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.compute_lambda, -1)

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.compute_lambda, 2048)

    def test_spectrum(self):
        pixels = {
            1:2048, # CCD - 2048
            2:1024, # CCD - 1024
            3:2048, # PDA - 2048
            4:1024, # PDA - 1024
            5:512,  # InGaAs - 512
            6:1024  # InGaAs - 1024
                    # PDA - 3600 (don't know the detector type for this one)
        }[self.spectro.get_config()['det_type']]
        self.assertEqual(len(self.spectro.read_spectrum()), pixels,
                         'should be {} pixel counts'.format(pixels))

    def test_get_stored_bytes(self):
        self.assertRaises(stellarnet.ArgRangeError, self.spectro.get_stored_bytes, 0x01)

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.get_stored_bytes, 0x100)

    def test_get_stored_string(self):
        self.assertRaises(stellarnet.ArgRangeError, self.spectro.get_stored_string, 0x01)

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.get_stored_string, 0x100)

    def test_set_stored_bytes(self):
        self.assertRaises(stellarnet.ArgRangeError, self.spectro.set_stored_bytes, 0x01, bytearray(0x20))

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.set_stored_bytes, 0x100, bytearray(0x20))

        self.assertRaises(stellarnet.ArgRangeError, self.spectro.set_stored_bytes, 0x00, bytearray(0x1f))
        
    def test_get_device_id(self):
        device_id = self.spectro.get_device_id()
        self.assertIsNotNone(device_id, 'device_id should not be None')
        self.assertGreater(len(device_id), 0, 'device_id should not be empty')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStellarNet)
    unittest.TextTestRunner(verbosity=2).run(suite)
