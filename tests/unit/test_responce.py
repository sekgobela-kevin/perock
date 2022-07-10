import unittest
from perock import responce


class BytesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "Bytes of text"
        self.bytes = responce.Bytes(self.text)

    def test_get_bytes(self):
        self.assertEqual(self.bytes.get_bytes(), self.text.encode())

    def test_enable_contains_strict(self):
        self.bytes.enable_contains_strict()

    def test_disable_contains_strict(self):
        self.bytes.disable_contains_strict()


    def test_to_bytes(self):
        self.assertEqual(self.bytes.to_bytes(self.text), self.text.encode())
        self.assertEqual(
            self.bytes.to_bytes(self.text.encode()), 
            self.text.encode()
        )

    def test_to_text(self):
        self.assertEqual(self.bytes.to_text(self.text), self.text)
        self.assertEqual(
            self.bytes.to_text(self.text.encode()), 
            self.text
        )

    def test_contains_filter(self):
        filtered = list(self.bytes.contains_filter(
            self.text.encode(),
            ["text", "not"])
        )
        self.assertEqual(filtered, ["text"])

    def test_contains_any(self):
        self.assertTrue(self.bytes.contains_any(["text", "Bytes"]))
        self.assertTrue(self.bytes.contains_any(["text", "not"]))
        self.assertFalse(self.bytes.contains_any(["noa", "dsd"]))
        self.assertFalse(self.bytes.contains_any([]))

    def test_contains_all(self):
        self.assertTrue(self.bytes.contains_all(["text", "Bytes"]))
        self.assertFalse(self.bytes.contains_all(["text", "not"]))
        self.assertFalse(self.bytes.contains_all([]))

    def test_contains_iterator(self):
        self.bytes.enable_contains_strict()
        self.assertFalse(self.bytes.contains_iterator(["text", "not"]))
        self.bytes.disable_contains_strict()
        self.assertTrue(self.bytes.contains_iterator(["text", "not"]))

    def test_lower(self):
        lower = self.bytes.lower()
        self.assertTrue(lower.get_bytes(), self.text.encode().lower())

    def test_upper(self):
        upper = self.bytes.upper()
        self.assertTrue(upper.get_bytes(), self.text.encode().upper())



class BytesCompareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "Bytes of text"
        self.success_text = "success text"
        self.failure_text = "fail failure text"
        self.error_text = "error wrong text"
        self.target_error_text = "target error text"
        self.client_error_text = "client error text"
        self.not_found_error_text = "not found error text"
        self.access_denied_error_text = "access denied error text"
        self.wait_error_text = "wait for while text"

        self.bytes_compare = responce.BytesCompare(self.text.encode())

        self.success_bytes_compare = responce.BytesCompare(
        self.success_text.encode())
        self.failure_bytes_compare = responce.BytesCompare(
        self.failure_text.encode())

        self.error_bytes_compare = responce.BytesCompare(
        self.error_text.encode())
        self.wait_error_bytes_compare = responce.BytesCompare(
        self.wait_error_text.encode())

        self.target_error_bytes_compare = responce.BytesCompare(
        self.target_error_text.encode())
        self.client_error_bytes_compare = responce.BytesCompare(
        self.client_error_text.encode())

        self.not_found_error_bytes_compare = responce.BytesCompare(
        self.not_found_error_text.encode())
        self.access_denied_error_bytes_compare = responce.BytesCompare(
        self.access_denied_error_text.encode())


        self.success_bytes_compare.set_success_bytes_strings(["success"])
        self.failure_bytes_compare.set_failure_bytes_strings(["failure"])
        self.error_bytes_compare.set_error_bytes_strings(["error"])

        self.target_error_bytes_compare.set_target_error_bytes_strings(
        ["target error"])
        self.client_error_bytes_compare.set_client_error_bytes_strings(
        ["client error"])
        self.not_found_error_bytes_compare.set_not_found_error_bytes_strings(
        ["not found"])

        self.access_denied_error_bytes_compare.set_access_denied_error_bytes_strings(
        ["access denied"])
        self.wait_error_bytes_compare.set_wait_error_bytes_strings(["wait"])


    def test__create_responce_bytes(self):
        self.assertIsInstance(
            self.bytes_compare._create_responce_bytes(b""),
            responce.Bytes
        )

    def test_enable_contains_strict(self):
        self.bytes_compare.enable_contains_strict()

    def test_disable_contains_strict(self):
        self.bytes_compare.disable_contains_strict()


    def test_responce_bytes(self):
        self.assertIsInstance(self.bytes_compare.responce_bytes, responce.Bytes)

    def test_set_success_bytes_strings(self):
        self.bytes_compare.set_success_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.success())
        self.bytes_compare.set_success_bytes_strings([])
        self.assertFalse(self.bytes_compare.success())

    def test_set_failure_bytes_strings(self):
        self.bytes_compare.set_failure_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.failure())
        self.bytes_compare.set_failure_bytes_strings([])
        self.assertFalse(self.bytes_compare.failure())

    def test_set_error_bytes_strings(self):
        self.bytes_compare.set_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.error())
        self.bytes_compare.set_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.error())


    def test_set_wait_error_bytes_strings(self):
        self.bytes_compare.set_wait_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.wait_error())
        self.bytes_compare.set_wait_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.wait_error())

    def test_set_not_found_error_bytes_strings(self):
        self.bytes_compare.set_not_found_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.not_found_error())
        self.bytes_compare.set_not_found_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.not_found_error())

    def test_set_access_denied_error_bytes_strings(self):
        self.bytes_compare.set_access_denied_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.access_denied_error())
        self.bytes_compare.set_access_denied_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.access_denied_error())


    def test_set_target_error_bytes_strings(self):
        self.bytes_compare.set_target_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.target_error())
        self.bytes_compare.set_target_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.target_error())

    def test_set_client_error_bytes_strings(self):
        self.bytes_compare.set_client_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.client_error())
        self.bytes_compare.set_client_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.client_error())

    def test_set_error_bytes_strings(self):
        self.bytes_compare.set_error_bytes_strings(["Bytes"])
        self.assertTrue(self.bytes_compare.error())
        self.bytes_compare.set_error_bytes_strings([])
        self.assertFalse(self.bytes_compare.error())



    def test_contains_iteraror(self):
        self.assertTrue(self.bytes_compare.contains_iteraror(["Bytes"]))
        self.assertFalse(self.bytes_compare.contains_iteraror(["notnot"]))
        

    def test_success(self):
        self.assertTrue(self.success_bytes_compare.success())
        self.assertFalse(self.bytes_compare.success())

    def test_failure(self):
        self.assertTrue(self.failure_bytes_compare.failure())
        self.assertFalse(self.bytes_compare.failure())


    def test_wait_error(self):
        self.assertTrue(self.wait_error_bytes_compare.wait_error())
        self.assertFalse(self.bytes_compare.wait_error())


    def test_not_found_error(self):
        self.assertTrue(self.not_found_error_bytes_compare.not_found_error())
        self.assertFalse(self.bytes_compare.not_found_error())

    def test_access_denied_error(self):
        error = self.access_denied_error_bytes_compare.access_denied_error()
        self.assertTrue(error)
        self.assertFalse(self.bytes_compare.access_denied_error())

    def test_target_error(self):
        self.assertTrue(self.wait_error_bytes_compare.wait_error())
        self.assertFalse(self.bytes_compare.wait_error())

    def test_client_error(self):
        self.assertTrue(self.client_error_bytes_compare.client_error())
        self.assertFalse(self.bytes_compare.client_error())

    def test_error(self):
        self.assertTrue(self.client_error_bytes_compare.client_error())
        self.assertFalse(self.bytes_compare.client_error())

