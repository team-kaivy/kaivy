########################################################################################################################
#                                                                                                                      #
#                                             This file is part of kAIvy                                               #
#                                                                                                                      #
#                                      Copyright (c) 2019-2021 by the kAIvy team and contributors                                      #
#                                                                                                                      #
########################################################################################################################

from kaivy.dialogs.message_box import MessageBox
from kaivy.common.labeled_checkbox import LabeledCheckbox


class TermsAndConditionsDialog(MessageBox):
    """
    The terms and conditions dialog shows a legal text which needs to be confirmed by a checkbox, a confirmation
    button and a cancel button. The confirmation button can only be pressed when the checkbox was ticked.
    """

    def __init__(self, legal_text="YourText", title="Terms and conditions",
                 checkbox_text="I accept these terms and conditions",
                 accept_text="Continue", cancel_text="Cancel", text_width=900):
        """
        Initializer
        :param legal_text: The terms and conditions to be displayed
        :param title: The dialog's title
        :param checkbox_text: The checkbox text, e.g. "I accept these terms and conditions"
        :param accept_text: The text for the accept button
        :param cancel_text: The text for the cancel button
        :param text_width: The space to be reserved for the text width in pixel
        """
        self.checkbox = LabeledCheckbox(size_hint=(None, None), size=(32, 32))
        self.checkbox.set_text(checkbox_text)
        super().__init__(title, text=legal_text, buttons=[accept_text, cancel_text], custom_view=self.checkbox,
                         text_width=text_width, close_index=1)

        self.get_button(0).disabled = True
        self.checkbox.on_checkbox_state = self.check_state_change

    def check_state_change(self, bt, value):
        self.get_button(0).disabled = not value


if __name__ == '__main__':  # Most minimal test application
    from kivy.base import runTouchApp
    from kivy.uix.gridlayout import GridLayout
    from kivy.core.window import Window

    legal_text = \
        "I wish to continue with ... and expressly agree to the following:\n\n" \
        "• This\n\n" \
        "• That\n\n" \
        "• And even more...\n"

    dialog = TermsAndConditionsDialog(legal_text=legal_text)
    layout = GridLayout(cols=3)
    Window.add_widget(layout)
    Window.size = (1280, 800)
    dialog.show()

    runTouchApp()
