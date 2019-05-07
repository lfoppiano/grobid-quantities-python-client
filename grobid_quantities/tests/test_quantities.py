import unittest

from grobid_quantities.quantities import QuantitiesClient


class QuantitiesTest(unittest.TestCase):

    def setUp(self):
        self.target = QuantitiesClient()

    # def testProcess_text(self):
    #     result = self.target.process_text(text="We introduce in this paper D-SPACES, an implementation of constraint "
    #                                            "systems with space and extrusion operators. Constraint systems are "
    #                                            "algebraic models that allow for a semantic language-like "
    #                                            "representation of information in systems where the concept of space is "
    #                                            "a primary structural feature. We give this information mainly an "
    #                                            "epistemic interpretation and consider various agents as entities "
    #                                            "acting upon it. D-SPACES is coded as a c++11 library providing "
    #                                            "implementations for constraint systems, space functions and extrusion "
    #                                            "functions. The interfaces to access each implementation are minimal "
    #                                            "and thoroughly documented. D-SPACES also provides property-checking "
    #                                            "methods as well as an implementation of a specific type of constraint "
    #                                            "systems (a boolean algebra). This last implementation serves as an "
    #                                            "entry point for quick access and proof of concept when using these "
    #                                            "models. Furthermore, we offer an illustrative example in the form of a "
    #                                            "small social network where users post their beliefs and utter their "
    #                                            "opinions ")
    #     assert result is not None or ""
    #     assert result[0] is 200
    #
    # def testProcess_text2(self):
    #     result = self.target.process_text(text="I lost two minutes.")
    #     assert result is not None or ""
    #     assert result[0] is 200
    #
    #     print(result[1])

    # def test_parse_measures(self):
    #     query = {"from": "10", "to": "20", "unit": "km"}
    #
    #     result = self.target.parse_measures(str(query))
    #     assert result[0] is 200
    #     assert result is not None or ""
    #
    #     print(result[1])


if __name__ == '__main__':
    unittest.main()
