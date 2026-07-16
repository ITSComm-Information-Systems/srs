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

    def test_text_size_settings_are_accessible_and_default_to_100_percent(self):
        self.assertIn("--srs-chatbot-text-size:100%;", self.template)
        self.assertIn('aria-label="Open chatbot settings"', self.template)
        self.assertIn('aria-expanded="false"', self.template)
        self.assertIn('aria-controls="srs-chatbot-settings"', self.template)
        self.assertIn('id="srs-chatbot-settings"', self.template)
        self.assertIn('aria-label="Chatbot settings"', self.template)
        self.assertIn('aria-label="Close chatbot settings"', self.template)
        self.assertIn("<legend>Text size</legend>", self.template)

    def test_all_requested_text_size_options_are_available(self):
        for size in ["60", "80", "100", "110", "120", "150"]:
            self.assertIn(f'name="srs-chatbot-text-size" value="{size}"', self.template)


class ChatbotScriptTests(SimpleTestCase):
    def setUp(self):
        self.script = CHATBOT_SCRIPT.read_text()

    def test_text_size_selection_updates_and_persists(self):
        self.assertIn("TEXT_SIZE_DEFAULT = '100'", self.script)
        self.assertIn("TEXT_SIZE_STORAGE_KEY = 'srsChatbotTextSize'", self.script)
        self.assertIn("window.localStorage.getItem(TEXT_SIZE_STORAGE_KEY)", self.script)
        self.assertIn("window.localStorage.setItem(TEXT_SIZE_STORAGE_KEY, size)", self.script)
        self.assertIn("windowEl.style.setProperty('--srs-chatbot-text-size'", self.script)
        self.assertIn("input.checked = input.value === selectedSize", self.script)
        self.assertIn("applyTextSize(getStoredTextSize(), false)", self.script)

    def test_settings_panel_keyboard_accessibility(self):
        self.assertIn("settingsToggle.addEventListener('click'", self.script)
        self.assertIn("settingsClose.addEventListener('click'", self.script)
        self.assertIn("settingsToggle.setAttribute('aria-expanded'", self.script)
        self.assertIn("event.key === 'Escape'", self.script)
        self.assertIn("setSettingsOpen(false)", self.script)
