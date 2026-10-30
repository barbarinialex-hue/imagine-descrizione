import base64
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from analisi import analizza, prepara_immagine, valida_risposta, scegli_modello
R = dict(coerente=True, descrizione='Tazza.', motivazione='Compatibile.', anomalie=[], limiti=[])
class Tests(unittest.TestCase):
    def test_valid(self):
        for v in (True, False, None):
            r = dict(R, coerente=v)
            self.assertEqual(valida_risposta(json.dumps(r)), r)
    def test_invalid(self):
        for s in ('{}', '[]', 'abc', json.dumps(dict(R, coerente=1)), json.dumps(dict(R, extra=1)), json.dumps(dict(R, anomalie=[1]))):
            with self.subTest(s=s), self.assertRaises(ValueError):
                valida_risposta(s)
    def test_image(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'foto.png'
            Image.new('RGB', (2000,1200)).save(p)
            data = prepara_immagine(p)
            with Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))) as img:
                self.assertEqual(img.size, (1024,614))
            p.write_text('invalid')
            with self.assertRaises(ValueError): prepara_immagine(p)
    @patch('analisi.request_json')
    def test_no_paid_fallback(self, api):
        api.return_value = {'data':[{'id':'vendor/paid','architecture':{'input_modalities':['image']},'supported_parameters':['structured_outputs']}]}
        with self.assertRaises(ValueError): scegli_modello('key')
        self.assertEqual(scegli_modello('key', 'vendor/paid'), 'vendor/paid')
    @patch('analisi.prepara_immagine', return_value='data:image/jpeg;base64,TEST')
    @patch('analisi.scegli_modello', return_value='test:free')
    @patch('analisi.request_json')
    def test_flow(self, api, model, image):
        api.return_value = {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(R)}}]}
        self.assertEqual(analizza('a.png', 'Tazza', 'key'), R)
        self.assertTrue(api.call_args.args[2]['provider']['require_parameters'])
        api.return_value['choices'][0]['finish_reason']='length'
        with self.assertRaises(ValueError): analizza('a.png', key='key')
