"""
Resident app
"""

from flexx import event, flx
from api_wrapper import get_rid_status, get_credential_types

with open('style.css') as f:
    style = f.read()

flx.assets.associate_asset(__name__, 'style.css', style)

class Resident(flx.Widget):

    def init(self):
        with flx.VBox(css_class='form'):
            with flx.HBox():
                flx.Label(text='Resident HelpDesk', css_class='title')
                flx.ImageWidget(flex=1, source='https://www.omidyarnetwork.in/wp-content/uploads/2019/05/mosip.png')
            with flx.HBox():
                with flx.VBox():
                    self.labela = flx.Label(text='RID status', css_class='left_label_selected')
                    self.labelb = flx.Label(text='green', css_class='left_label')
                    self.labelc = flx.Label(text='blue', css_class='left_label')
                    flx.Widget(flex=1)  # space filler
                with flx.StackLayout(flex=1) as self.stack:
                    self.labela.w = flx.Widget(style='background:#a00;')
                    self.labelb.w = flx.Widget(style='background:#0a0;')
                    self.labelc.w = flx.Widget(style='background:#00a;')
            flx.Label(text='(c) MOSIP www.mosip.io')
        self.current_label = self.labela

    @event.reaction('labela.pointer_down', 'labelb.pointer_down', 'labelc.pointer_down')
    def _stacked_current(self, *events):
        cur = self.current_label
        cur.set_css_class('left_label')  # Reset the color
        cur  = events[-1].source  # New selected label
        self.stack.set_current(cur.w)
        cur.set_css_class('left_label_selected')
        self.current_label = cur

def main(argv):

    unused = argv # noqa

    app = flx.App(Resident,
                  title='Resident Portal') # , icon=ico)
    # app.export('test.html', link=0)
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
