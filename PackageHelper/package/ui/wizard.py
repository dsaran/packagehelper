from kiwi.ui.wizard import PluggableWizard

class Wizard(PluggableWizard):


    def __init__(self, title, first_step, size=None, edit_mode=False):
        PluggableWizard.__init__(self, title, first_step, size=size, edit_mode=edit_mode)

    def on_next_button__clicked(self, button):
        if not self._current.validate_step():
            return

        if not self._current.has_next_step():
            # This is the last step
            self._change_step()
            return

        self._change_step(self._current.next_step())

    def on_previous_button__clicked(self, button):
        self._change_step(self._current.previous_step(), process=False)

    def _change_step(self, step=None, process=True):
        if step is None:
            # This is the last step and we can finish the job here
            self.finish()
            return
        step.show()
        self._current = step
        self._refresh_slave()
        if step.header:
            self.header_lbl.show()
            self.header_lbl.set_text(step.header)
        else:
            self.header_lbl.hide()
        self.update_view()
        if process:
            self._current.post_init()

