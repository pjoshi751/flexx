"""
Resident app
"""

from flexx import event, flx
from api_wrapper import get_rid_status, get_credential_types

with open('style.css') as f:
    style = f.read()

flx.assets.associate_asset(__name__, 'style.css', style)

class ResidentMain(flx.PyComponent):

    def __init__(self, *args, **kwargs):
        self.__kwargs = kwargs
        super().__init__(*args, **kwargs)

    def init(self):
        super().init()
        self.resident = Resident(**self.__kwargs)

    @flx.reaction('resident.rid_submitted')
    def handle_rid_submitted(self, *events):
        rid = events[-1]['rid'] 
        status = get_rid_status(rid)
        self.resident.set_status(f'Status: {status}')

class Resident(flx.Widget):

    def init(self):
        with flx.VBox():
            with flx.HBox():
                flx.Label(text='Resident HelpDesk', css_class='sitetitle')
                flx.ImageWidget(flex=1, source='https://www.omidyarnetwork.in/wp-content/uploads/2019/05/mosip.png', css_class='logo')
            with flx.HBox():
                with flx.VBox():
                    self.label_a = flx.Label(text='RID status', css_class='left_label_selected')
                    self.label_b = flx.Label(text='Auth lock', css_class='left_label')
                    self.label_c = flx.Label(text='eCard', css_class='left_label')
                    self.label_d = flx.Label(text='VID', css_class='left_label')
                    self.label_e = flx.Label(text='Auth history', css_class='left_label')
                    flx.Widget(flex=1)  # space filler
                with flx.StackLayout(flex=1) as self.stack:
                    with flx.FormLayout(css_class='form') as self.label_a.w:
                        self.subtitle = flx.Label(text='RID status', css_class='subtitle')
                        self.rid = \
                          flx.LineEdit(title='RID', text='')
                        self.submit = flx.Button(text='Submit')

                    self.label_b.w = flx.Widget(style='background:#fff')
                    self.label_c.w = flx.Widget(style='background:#fff;')
                    self.label_d.w = flx.Widget(style='background:#fff;')
                    self.label_e.w = flx.Widget(style='background:#fff;')
            flx.Label(text='(c) MOSIP www.mosip.io', css_class='sitefooter')

        self.current_label = self.label_a

    @flx.action
    def set_status(self, text):
        global window
        window.alert(text)

    @flx.emitter
    def rid_submitted(self, rid):
        return {'rid': rid}

    @flx.reaction('submit.pointer_click')
    def handle_rid_submit(self, *events):
        unused = events # noqa
        self.rid_submitted(self.rid.text)

    @event.reaction('label_a.pointer_down', 'label_b.pointer_down', 'label_c.pointer_down', 'label_d.pointer_down',
                    'label_e.pointer_down')
    def _stacked_current(self, *events):
        cur = self.current_label
        cur.set_css_class('left_label')  # Reset the color
        cur  = events[-1].source  # New selected label
        self.stack.set_current(cur.w)
        cur.set_css_class('left_label_selected')
        self.current_label = cur

def main(argv):

    unused = argv # noqa

    app = flx.App(ResidentMain,
                  title='Resident Portal') # , icon=ico)
    # app.export('test.html', link=0)
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
