
import app.ticket_gen as ticket_gen
import unittest
from unittest.mock import Mock, patch


class TestTicketGenMethods(unittest.TestCase):
    def setUp(self):
        pass

    @patch('random.choice')
    def test_get_client(self, random_choice_mock):
        random_choice_mock.side_effect = [
            "A", "B", "C", "D", "E", "F", "1", "2", "3", "4", "5", "6", "7", "8"
        ]
        resp = ticket_gen.get()

        # Assume default length is 8.
        self.assertEqual(resp, "ABCDEF12")


if __name__ == '__main__':
    unittest.main()
