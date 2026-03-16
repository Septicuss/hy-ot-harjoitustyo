import unittest
from kassapaate import Kassapaate
from maksukortti import Maksukortti

class TestKassapaate(unittest.TestCase):
    def setUp(self):
        self.kortti = Maksukortti(100000)
        self.kortti_pieni = Maksukortti(100)
        self.kateinen = 100000
        self.kateinen_pieni = 100
        self.kassapaate = Kassapaate()

    def test_rahaa_alussa(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)

    def test_lounaita_alussa(self):
        self.assertEqual(self.kassapaate.maukkaat, 0)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_eurot_oikein(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000.00)

    def test_korttimaksu_toimii(self):
        self.kassapaate.syo_edullisesti_kortilla(self.kortti)
        self.kassapaate.syo_maukkaasti_kortilla(self.kortti)
        total = self.kassapaate.edulliset + self.kassapaate.maukkaat
        self.assertEqual(total, 2)

    def test_kassa_ei_muutu_kortilla(self):
        self.kassapaate.syo_edullisesti_kortilla(self.kortti)
        self.kassapaate.syo_maukkaasti_kortilla(self.kortti)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)

    def test_korttimaksu_onnistuu_oikein_edullisesti(self):
        tulos = self.kassapaate.syo_edullisesti_kortilla(self.kortti)
        self.assertTrue(tulos)
        self.assertEqual(self.kortti.saldo, 99760)

    def test_korttimaksu_onnistuu_oikein_maukkaasti(self):
        tulos = self.kassapaate.syo_maukkaasti_kortilla(self.kortti)
        self.assertTrue(tulos)
        self.assertEqual(self.kortti.saldo, 99600)

    def test_kortti_liian_pieni_saldo_toimii(self):
        edullinen = self.kassapaate.syo_edullisesti_kortilla(self.kortti_pieni)
        maukas = self.kassapaate.syo_maukkaasti_kortilla(self.kortti_pieni)

        self.assertFalse(edullinen)
        self.assertFalse(maukas)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_kortille_lataaminen_onnistuu(self):
        self.kassapaate.lataa_rahaa_kortille(self.kortti, 100)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000+100)
        self.assertEqual(self.kortti.saldo, 100000+100)

    def test_kortille_ei_voi_ladata_negatiivista_summaa(self):
        self.kassapaate.lataa_rahaa_kortille(self.kortti, -100)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
        self.assertEqual(self.kortti.saldo, 100000)

    def test_kateismaksu_toimii(self):
        self.kassapaate.syo_edullisesti_kateisella(self.kateinen)
        self.kassapaate.syo_maukkaasti_kateisella(self.kateinen)
        total = self.kassapaate.edulliset + self.kassapaate.maukkaat
        self.assertEqual(total, 2)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 100640)

    def test_kateinen_edullisen_vaihtoraha_oikea(self):
        self.assertEqual(self.kassapaate.syo_edullisesti_kateisella(self.kateinen), 99760)

    def test_kateinen_maukkaan_vaihtoraha_oikea(self):
        self.assertEqual(self.kassapaate.syo_maukkaasti_kateisella(self.kateinen), 99600)

    def test_liian_pieni_kateinen_toimii_oikein(self):
        edullinen = self.kassapaate.syo_edullisesti_kateisella(self.kateinen_pieni)
        maukas = self.kassapaate.syo_maukkaasti_kateisella(self.kateinen_pieni)

        self.assertEqual(self.kassapaate.kassassa_rahaa, 100000)
        self.assertEqual(edullinen, self.kateinen_pieni)
        self.assertEqual(maukas, self.kateinen_pieni)