from pathlib import Path

from django.test import SimpleTestCase


BASE_TEMPLATE = Path(__file__).resolve().parent / "templates" / "base.html"
CHATBOT_SCRIPT = Path(__file__).resolve().parent / "static" / "js" / "srs_chatbot.js"


class ChatbotTemplateTests(SimpleTestCase):
    def setUp(self):
        self.template = BASE_TEMPLATE.read_text()

    def test_support_options_are_ordered_and_renamed(self):
        telephony_title = "Telephone, Data, &amp; Video Support"
        its_title = "Other ITS Services Support"

        self.assertIn(telephony_title, self.template)
        self.assertIn(its_title, self.template)
        self.assertLess(self.template.index(telephony_title), self.template.index(its_title))
        self.assertNotIn("<strong>Telephony Support</strong>", self.template)
        self.assertNotIn("<strong>IT Services Support</strong>", self.template)
