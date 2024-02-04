from datetime import datetime
from src.backend.app.tests.utility import UnitTestMain
from src.backend.app.schemas.series import SeriesBaseSchema, SeriesCreateSchema
from fastapi.encoders import jsonable_encoder as jsonify

"""
Testing Match
    start_date
    end_date
    host
"""


class SeriesTest(UnitTestMain):

    def test_get_one_series(self):
        # Testing series creation and fetching for one series.
        s = SeriesCreateSchema(
            start_date=datetime.now(), end_date=datetime.now(), host='Europe - Finland'
        )

        response = self.client.post("/api/series/", json=jsonify(s))
        self.assertEqual(response.status_code, 201)

        series_output = response.json()
        series_output = SeriesBaseSchema(**series_output)
        response = self.client.get(f"/api/series/{series_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_update_series(self):
        # Testing series creation and fetching for one series.
        t = SeriesCreateSchema(start_date=datetime.now(), end_date=datetime.now(), host='F')
        r = self.client.post("/api/series/", json=jsonify(t))
        t = SeriesBaseSchema(**r.json())

        t.host = 'SENEGAL'
        _ = self.client.put(f"/api/series/{t.id}", json=jsonify(t))
        r = self.client.get(f"/api/series/{t.id}")
        output = r.json()
        output = SeriesBaseSchema(**output)
        self.assertEqual(output.host, t.host)
        self.assertEqual(r.status_code, 200)

    def test_delete_series(self):
        # Testing series creation and fetching for one series.
        t = SeriesCreateSchema(start_date=datetime.now(), end_date=datetime.now(), host='F')
        r = self.client.post("/api/series/", json=jsonify(t))
        t = SeriesBaseSchema(**r.json())

        f = self.client.delete(f"/api/series/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/series/{t.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_series(self):
        # Testing series creation and fetching for multiple series.
        t = SeriesCreateSchema(start_date=datetime.now(), end_date=datetime.now(), host='F')
        e = SeriesCreateSchema(start_date=datetime.now(), end_date=datetime.now(), host='F')
        response = self.client.post(f"/api/series/", json=jsonify(t))
        response = self.client.post(f"/api/series/", json=jsonify(e))

        response = self.client.get(f"/api/series/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_get_matches(self):
        pass

