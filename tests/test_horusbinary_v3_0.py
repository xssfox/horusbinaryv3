import unittest
import asn1tools
import logging
import json
import datetime

class TestHorusBinaryV3_0(unittest.TestCase):
    def setUp(self):
        self.uper = asn1tools.compile_files("./HorusBinaryV3.asn1", codec="uper")

    # This tests building a payload with practically every feature
    def test_bells_and_whistles(self):
        self.maxDiff = 4000
        data = { # This is an example packet that will be way too big, but it highlights all the features
            "payloadCallsign": "abcDEF-0123abc-",
            "sequenceNumber": 65535,
            "timeOfDaySeconds": 86400,
            "latitude": 90,
            "longitude": -180,
            "altitudeMeters": 50000,
            "velocityHorizontalKilometersPerHour": 255,
            "gnssSatellitesVisible": 31,
            "ascentRateCentimetersPerSecond": 32767,
            "pressurehPa": 127,
            "temperatureCelsius": {
                "internal": -127,
                "external": 127,
                "custom1": -127,
                "custom2": 127,
                
            },
            "humidityPercentage":[0,100,0,100],
            "milliVolts": {
                "battery": 0,
                "solar": 16383,
                "custom1": 0,
                "custom2": 16383,
                },
            "counts": [1,100,1000,10000,100000,1000000,1000000],
            "safeMode": True,
            "powerSave": False,
            "gpsLock": True,

            "extraSensors": [
                {
                    "name": "hbk8359hbk8359hbk835", 
                    "values": ("horusInt", [1,2]) 
                },
                {
                    "name": "crm114",
                    "values": ("horusBool", {
                        "b0": True,"b1": True,"b2": True,"b3": True,"b4": True,"b5": True,"b6": True,"b7": True
                    })
                },
                { 
                    "values": ("horusStr", "ABCEDFGEFGH123324asdbkjbsdg")
                },
                {
                    "values": ("horusReal",[0.1234,1232342345234234,0.1234,1232342345234234])
                }
            ],
        }
        encoded = self.uper.encode("Telemetry",data)
        decoded = self.uper.decode("Telemetry", encoded)

        logging.debug(f"Length: {len(encoded)} Data: {encoded.hex()}")

        self.assertDictEqual(data, decoded)

    def test_bells_and_whistles_extend(self):
        data = { # This is an example packet that will be way too big, but it highlights all the features
            "payloadCallsign": "abcDEF-0123abc-",
            "sequenceNumber": 65535,
            "timeOfDaySeconds": 86400,
            "latitude": 90,
            "longitude": -180,
            "altitudeMeters": 50000,
            "velocityHorizontalKilometersPerHour": 255,
            "gnssSatellitesVisible": 31,
            "ascentRateCentimetersPerSecond": 32767,
            "pressurehPa": 127,
            "temperatureCelsius": {
                "internal": -127,
                "external": 127,
                "custom1": -127,
                "custom2": 127,
                
            },
            "humidityPercentage":[0,100,0,100],
            "milliVolts": {
                "battery": 0,
                "solar": 16383,
                "custom1": 0,
                "custom2": 16383,
                },
            "counts": [1,100,1000,10000,100000,1000000,1000000],
            "safeMode": True,
            "powerSave": False,
            "gpsLock": True,

            "extraSensors": [
                {
                    "name": "hbk8359hbk8359hbk835", 
                    "values": ("horusInt", [1,2]) 
                },
                {
                    "name": "crm114",
                    "values": ("horusBool", {
                        "b0": True,"b1": True,"b2": True,"b3": True,"b4": True,"b5": True,"b6": True,"b7": True
                    })
                },
                { 
                    "values": ("horusStr", "ABCEDFGEFGH123324asdbkjbsdg")
                },
                {
                    "values": ("horusReal",[0.1234,1232342345234234,0.1234,1232342345234234])
                }
            ],
        }
        encoded = self.uper.encode("Telemetry",data)
        
        # extend the spec by adding some extra fields to the end
        with open("./HorusBinaryV3.asn1","r") as f:
            horus_def = f.read()
        horus_def = horus_def.replace("...","""
        ...,
        testExtend1 [19] EXPLICIT INTEGER (0..127),
        testExtend2 [20] EXPLICIT IA5String -- MARKER
        """,1)
        extended_uper = asn1tools.compile_string(horus_def, codec="uper")
        decoded = extended_uper.decode("Telemetry", encoded)

        # Test that we can still read old data
        self.assertDictEqual(data, decoded)

        # Test that old encoders can read new data
        extended_data = dict(data)
        extended_data["testExtend1"] = 99
        extended_data["testExtend2"] = "test string"
        extended_encoded = extended_uper.encode("Telemetry",extended_data)
        logging.debug(f"Length: {len(extended_encoded)} Data: {extended_encoded.hex()}")
        extended_decoded = self.uper.decode("Telemetry", extended_encoded)
        self.assertDictEqual(data, extended_decoded)
        
        # Test we can actually decode the new values
        extended_decoded_full = extended_uper.decode("Telemetry", extended_encoded)
        self.assertDictEqual(extended_data, extended_decoded_full)
        

        # Test extending further
        horus_def = horus_def.replace("-- MARKER",""",
        testExtend3 [21] EXPLICIT INTEGER 
        """,1)
        extended_more_uper = asn1tools.compile_string(horus_def, codec="uper")
        decoded_more = extended_more_uper.decode("Telemetry", encoded)

        # Test that we can still read old data
        self.assertDictEqual(data, decoded_more)

        # Test that we can read 2nd revision data
        decoded_more_2 = extended_more_uper.decode("Telemetry", extended_encoded)
        self.assertDictEqual(extended_data, decoded_more_2)

        # Test that the 3rd revision can read the third encoded
        extended_more_data = dict(extended_data)
        extended_more_data["testExtend3"] = 99
        
        extended_more_encoded = extended_more_uper.encode("Telemetry",extended_more_data)
        extended_more_decoded = extended_more_uper.decode("Telemetry",extended_more_encoded)
        self.assertDictEqual(extended_more_data, extended_more_decoded)

        # Test that the 2nd revision encoder can read the third revision data
        extended_more_2_decoded = extended_uper.decode("Telemetry",extended_more_encoded)
        self.assertDictEqual(extended_data, extended_more_2_decoded)


    def test_required_fields_small(self):
        data = { 
            "payloadCallsign": "abcDEF-0123abc-",
            "sequenceNumber": 65535,
            "timeOfDaySeconds": 86400,
            "latitude": 90,
            "longitude": -180,
            "altitudeMeters": 50000,
            "safeMode": True,
            "powerSave":False,
            "gpsLock": False
        }
        encoded = self.uper.encode("Telemetry",data)
        decoded = self.uper.decode("Telemetry", encoded)

        logging.debug(f"Length: {len(encoded)} Data: {encoded.hex()}")

        self.assertDictEqual(data, decoded)
        self.assertLessEqual(len(data), 30)


    def test_can_decode_known(self):
        # Ensure that we can decode an older packet and nothing has changed
        data = { # This is an example packet that will be way too big, but it highlights all the features
            "payloadCallsign": "abcDEF-0123abc-",
            "sequenceNumber": 65535,
            "timeOfDaySeconds": 86400,
            "latitude": 90,
            "longitude": -180,
            "altitudeMeters": 50000,
            "velocityHorizontalKilometersPerHour": 255,
            "gnssSatellitesVisible": 31,
            "ascentRateCentimetersPerSecond": 32767,
            "pressurehPa": 127,
            "temperatureCelsius": {
                "internal": -127,
                "external": 127,
                "custom1": -127,
                "custom2": 127,
                
            },
            "humidityPercentage":[0,100,0,100],
            "milliVolts": {
                "battery": 0,
                "solar": 16383,
                "custom1": 0,
                "custom2": 16383,
                },
            "counts": [1,100,1000,10000,100000,1000000,1000000],
            "safeMode": True,
            "powerSave": False,
            "gpsLock": True,
            "customData": b"meowmeow",

            "extraSensors": [
                {
                    "name": "hbk8359hbk8359hbk835", 
                    "values": ("horusInt", [1,2]) 
                },
                {
                    "name": "crm114",
                    "values": ("horusBool", {
                        "b0": True,"b1": True,"b2": True,"b3": True,"b4": True,"b5": True,"b6": True,"b7": True
                    })
                },
                { 
                    "values": ("horusStr", "ABCEDFGEFGH123324asdbkjbsdg")
                },
                {
                    "values": ("horusReal",[0.1234,1232342345234234,0.1234,1232342345234234])
                }
            ],
        }
        decoded = self.uper.decode("Telemetry", bytes.fromhex("7fffa59a738f4000420c49669c0ffffa8c081c0009681e00116dc738f9a462a488314918a9220c52462a48832808080816535c5c2085ffd06c81124509952c50a962e18388101c4ab7ab963568b1eae62d84c0640fcb923a29c77984c000811833c3eeadce84c0640fcb923a29c77984c000811833c3eeadce9ffffffe0ffe01fc01fd80c803278001fff8001fffe010101640203e8022710030186a0030f4240030f4240086d656f776d656f770"))

        self.assertDictEqual(data, decoded)

    # Run through a test horus flight
    def test_itswindy(self):
        with open("./tests/ITSWINDY.json") as f:
            itswindy = json.load(f)
        max_length = 0
        for data in itswindy:
            seconds = (datetime.datetime.fromisoformat(data["datetime"]) - datetime.datetime.fromisoformat(data["datetime"]).replace(hour=0, minute=0, second=0, microsecond=0)).seconds
            to_encode = {
                "payloadCallsign": data['payload_callsign'],
                "sequenceNumber": data['frame'],
                "timeOfDaySeconds": seconds,
                "latitude": data['lat'],
                "longitude": data['lon'],
                "altitudeMeters": data['alt'],

                "gnssSatellitesVisible": data['sats'],
                "temperatureCelsius": {
                    "internal": int(data['temp']), 
                    "external": int(data['ext_temperature'])
                },
                "milliVolts": {"battery": int(data['batt']*1000)},
                "humidityPercentage": [data['ext_humidity']],
                "ascentRateCentimetersPerSecond": int(data["ascent_rate"]*100),
                "pressurehPa": int(data['ext_pressure']),
                "safeMode": True,
                "powerSave":False,
                "gpsLock": False
            }
            encoded = self.uper.encode("Telemetry",to_encode)
            if len(encoded) > max_length:
                max_length = len(encoded)
            decoded = self.uper.decode("Telemetry",encoded)

            self.assertEqual(decoded["gnssSatellitesVisible"],data['sats'])
            self.assertEqual(decoded["sequenceNumber"],data['frame'])
            self.assertEqual(decoded["altitudeMeters"],data['alt'])
            self.assertEqual(decoded["timeOfDaySeconds"],seconds)
            self.assertEqual(decoded["payloadCallsign"],data['payload_callsign'])
            self.assertEqual(decoded["latitude"],data['lat'])
            self.assertEqual(decoded["longitude"],data['lon'])
            self.assertEqual(decoded["temperatureCelsius"]["internal"],data['temp'])
            self.assertEqual(decoded["ascentRateCentimetersPerSecond"],int(data["ascent_rate"]*100))
            self.assertEqual(decoded["milliVolts"]["battery"],int(data['batt']*1000))
            self.assertLess(len(encoded),48)
            logging.debug(f"Length: {len(encoded)} Data: {encoded.hex()}")
        logging.debug(f"Max length was {max_length}")
        logging.debug(decoded)

if __name__ == "__main__":
    logging.getLogger().setLevel( logging.DEBUG )
    logging.basicConfig(format="%(funcName)s:%(lineno)s %(message)s")
    unittest.main()