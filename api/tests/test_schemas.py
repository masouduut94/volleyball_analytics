import unittest
from api.models import Rally
from api.schemas import RallyData


class TestJsonOutput(unittest.TestCase):
    def test_rally(self):
        p = Rally.get(1)
        print(p)
        results = RallyData.model_validate(p).model_dump()['spikes']
        self.assertIsInstance(list(results.keys())[0], int)
        # print(rally.model_dump())


if __name__ == '__main__':
    unittest.main()
