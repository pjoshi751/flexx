#!/usr/bin/env -S python3 -X utf8 -X dev


import flexx.flx as flx
from pscript import window
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
        get_credential_types()

class Resident(flx.Widget):

    def init(self):
        super().init()
        with flx.Widget(css_class='form'):
            with flx.VBox():
                with flx.FormLayout(css_class='dim'):
                    self.label = flx.Label(text='Resident Portal')
                    self.rid = \
                      flx.LineEdit(title='RID',
                                   text='')
                    flx.Label(text='')
                    self.submit = flx.Button(text='Submit')

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
