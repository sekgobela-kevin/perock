import unittest
from perock import responce


class TestResponceBytes(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "Bytes of text"
        self.responce_bytes = responce.ResponceBytes(self.text)

    def test_get_bytes(self):
        self.assertEqual(self.responce_bytes.get_bytes(), self.text.encode())

    def test_enable_contains_strict(self):
        self.responce_bytes.enable_contains_strict()

    def test_disable_contains_strict(self):
        self.responce_bytes.disable_contains_strict()


    def test_to_bytes(self):
        self.assertEqual(
            self.responce_bytes.to_bytes(self.text), self.text.encode()
        )
        self.assertEqual(
            self.responce_bytes.to_bytes(self.text.encode()), 
            self.text.encode()
        )

    def test_to_text(self):
        self.assertEqual(self.responce_bytes.to_text(self.text), self.text)
        self.assertEqual(
            self.responce_bytes.to_text(self.text.encode()), 
            self.text
        )

    def test_contains_filter(self):
        filtered = list(self.responce_bytes.contains_filter(
            self.text.encode(),
            ["text", "not"])
        )
        self.assertEqual(filtered, ["text"])

    def test_contains_any(self):
        self.assertTrue(self.responce_bytes.contains_any(["text", "Bytes"]))
        self.assertTrue(self.responce_bytes.contains_any(["text", "not"]))
        self.assertFalse(self.responce_bytes.contains_any(["noa", "dsd"]))
        self.assertFalse(self.responce_bytes.contains_any([]))

    def test_contains_all(self):
        self.assertTrue(self.responce_bytes.contains_all(["text", "Bytes"]))
        self.assertFalse(self.responce_bytes.contains_all(["text", "not"]))
        self.assertFalse(self.responce_bytes.contains_all([]))

    def test_contains_iterator(self):
        self.responce_bytes.enable_contains_strict()
        self.assertFalse(self.responce_bytes.contains_iterator(["text", "not"]))
        self.responce_bytes.disable_contains_strict()
        self.assertTrue(self.responce_bytes.contains_iterator(["text", "not"]))

    def test_lower(self):
        lower = self.responce_bytes.lower()
        self.assertTrue(lower.get_bytes(), self.text.encode().lower())

    def test_upper(self):
        upper = self.responce_bytes.upper()
        self.assertTrue(upper.get_bytes(), self.text.encode().upper())



class TestResponceBytesAnalyser(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "Bytes of text"
        self.target_reached_text = "target reached"
        self.success_text = "success text"
        self.failure_text = "fail failure text"
        self.error_text = "error wrong text"
        self.target_error_text = "target error text"
        self.client_error_text = "client error text"
        self.not_found_error_text = "not found error text"
        self.access_denied_error_text = "access denied error text"
        self.wait_error_text = "wait for while text"

        self.responce_analyser = responce.ResponceBytesAnalyser(
        self.text.encode())
        
        self.target_reached_responce_bytes = responce.ResponceBytesAnalyser(
        self.target_reached_text.encode())
        self.success_responce_bytes = responce.ResponceBytesAnalyser(
        self.success_text.encode())
        self.failure_responce_bytes = responce.ResponceBytesAnalyser(
        self.failure_text.encode())

        self.error_responce_bytes = responce.ResponceBytesAnalyser(
        self.error_text.encode())
        self.wait_error_responce_bytes = responce.ResponceBytesAnalyser(
        self.wait_error_text.encode())

        self.target_error_responce_bytes = responce.ResponceBytesAnalyser(
        self.target_error_text.encode())
        self.client_error_responce_bytes = responce.ResponceBytesAnalyser(
        self.client_error_text.encode())

        self.not_found_error_responce_bytes = responce.ResponceBytesAnalyser(
        self.not_found_error_text.encode())
        self.access_denied_error_responce_bytes = responce.ResponceBytesAnalyser(
        self.access_denied_error_text.encode())

        self.target_reached_responce_bytes.set_target_reached_bytes_strings(
        ["reached"])
        self.success_responce_bytes.set_success_bytes_strings(["success"])
        self.failure_responce_bytes.set_failure_bytes_strings(["failure"])
        self.error_responce_bytes.set_error_bytes_strings(["error"])

        self.target_error_responce_bytes.set_target_error_bytes_strings(
        ["target error"])
        self.client_error_responce_bytes.set_client_error_bytes_strings(
        ["client error"])
        self.not_found_error_responce_bytes.set_not_found_error_bytes_strings(
        ["not found"])

        self.access_denied_error_responce_bytes.\
            set_access_denied_error_bytes_strings(["access denied"])
        self.wait_error_responce_bytes.set_wait_error_bytes_strings(["wait"])


    def test__create_responce_bytes(self):
        self.assertIsInstance(
            self.responce_analyser._create_responce_bytes(),
            responce.ResponceBytes
        )

    def test_update(self):
        self.responce_analyser.update(b"bytes string")

    def test_enable_contains_strict(self):
        self.responce_analyser.enable_contains_strict()

    def test_disable_contains_strict(self):
        self.responce_analyser.disable_contains_strict()

    def test_set_target_reached_bytes_strings(self):
        self.responce_analyser.set_target_reached_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.target_reached())
        self.responce_analyser.set_target_reached_bytes_strings([])
        self.assertFalse(self.responce_analyser.target_reached())

    def test_set_success_bytes_strings(self):
        self.responce_analyser.set_success_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.success())
        self.responce_analyser.set_success_bytes_strings([])
        self.assertFalse(self.responce_analyser.success())

    def test_set_failure_bytes_strings(self):
        self.responce_analyser.set_failure_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.failure())
        self.responce_analyser.set_failure_bytes_strings([])
        self.assertFalse(self.responce_analyser.failure())

    def test_set_error_bytes_strings(self):
        self.responce_analyser.set_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.error())
        self.responce_analyser.set_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.error())


    def test_set_wait_error_bytes_strings(self):
        self.responce_analyser.set_wait_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.wait_error())
        self.responce_analyser.set_wait_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.wait_error())

    def test_set_not_found_error_bytes_strings(self):
        self.responce_analyser.set_not_found_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.not_found_error())
        self.responce_analyser.set_not_found_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.not_found_error())

    def test_set_access_denied_error_bytes_strings(self):
        self.responce_analyser.set_access_denied_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.access_denied_error())
        self.responce_analyser.set_access_denied_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.access_denied_error())


    def test_set_target_error_bytes_strings(self):
        self.responce_analyser.set_target_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.target_error())
        self.responce_analyser.set_target_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.target_error())

    def test_set_client_error_bytes_strings(self):
        self.responce_analyser.set_client_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.client_error())
        self.responce_analyser.set_client_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.client_error())

    def test_set_error_bytes_strings(self):
        self.responce_analyser.set_error_bytes_strings(["Bytes"])
        self.assertTrue(self.responce_analyser.error())
        self.responce_analyser.set_error_bytes_strings([])
        self.assertFalse(self.responce_analyser.error())



    def test_contains_iteraror(self):
        self.assertTrue(self.responce_analyser.contains_iteraror(["Bytes"]))
        self.assertFalse(self.responce_analyser.contains_iteraror(["notnot"]))
        
    def test_target_reached(self):
        self.assertTrue(self.target_reached_responce_bytes.target_reached())
        self.assertFalse(self.responce_analyser.target_reached())

    def test_success(self):
        self.assertTrue(self.success_responce_bytes.success())
        self.assertFalse(self.responce_analyser.success())

    def test_failure(self):
        self.assertTrue(self.failure_responce_bytes.failure())
        self.assertFalse(self.responce_analyser.failure())


    def test_wait_error(self):
        self.assertTrue(self.wait_error_responce_bytes.wait_error())
        self.assertFalse(self.responce_analyser.wait_error())


    def test_not_found_error(self):
        self.assertTrue(self.not_found_error_responce_bytes.not_found_error())
        self.assertFalse(self.responce_analyser.not_found_error())

    def test_access_denied_error(self):
        error = self.access_denied_error_responce_bytes.access_denied_error()
        self.assertTrue(error)
        self.assertFalse(self.responce_analyser.access_denied_error())

    def test_target_error(self):
        self.assertTrue(self.wait_error_responce_bytes.wait_error())
        self.assertFalse(self.responce_analyser.wait_error())

    def test_client_error(self):
        self.assertTrue(self.client_error_responce_bytes.client_error())
        self.assertFalse(self.responce_analyser.client_error())

    def test_error(self):
        self.assertTrue(self.client_error_responce_bytes.client_error())
        self.assertFalse(self.responce_analyser.client_error())

