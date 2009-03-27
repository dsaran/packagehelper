from kiwi.ui.wizard import PluggableWizard as KiwiPluggableWizard
from kiwi.ui.wizard import WizardStep as KiwiWizardStep

class Wizard(KiwiPluggableWizard):


    def __init__(self, title, first_step=None, steps=None, size=None, edit_mode=False, progressbar=None):
        if first_step:
            self.first_step = first_step
        elif steps:
            self.first_step = steps[0]
        else:
            raise Exception("You must supply first step or list of steps in order to create a Wizard instance")

        KiwiPluggableWizard.__init__(self, title, self.first_step, size=size, edit_mode=edit_mode)

        self.steps = steps

        if steps:
            self.progressbar = progressbar
            self._current_progress = 0
            self._size = len(self.steps)
            self._update_progress(0)
            step_list = [step.header for step in self.steps]
            self.progressbar.set_tooltip_text(" >> ".join(step_list))

    def on_next_button__clicked(self, button):
        if not self._current.validate_step():
            return

        if not self._current.has_next_step():
            # This is the last step
            self._change_step()
            return

        self._change_step(self._current.next_step())
        self._update_progress(1)

    def on_previous_button__clicked(self, button):
        self._change_step(self._current.previous_step(), process=False)
        self._update_progress(-1)

    def _change_step(self, step=None, process=True):
        if self._current:
            self._current.post_end()

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

    def _update_progress(self, step):
        if self.progressbar and self._size != None:
            self._current_progress += step
            self.progressbar.set_fraction(float(self._current_progress)/(self._size -1))
            self.progressbar.set_text("Passo %i de %i" % (self._current_progress+1, self._size))

class WizardStep(KiwiWizardStep):
    def post_end(self):
            """A virtual method that must be defined on child when it's
               necessary. This method will be called right before the change_step
               method on PluggableWizard for the current step.
           """


