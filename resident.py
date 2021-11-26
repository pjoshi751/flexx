#!/usr/bin/env -S python3 -X utf8 -X dev


import flexx.flx as flx
from pscript import window
from api_wrapper import get_rid_status

Styles = {
    'width': '40em',
    'margin': '0.5em',
    'themes': {
        'default': {
            0: {
                'bg': 'white',
                'fg': 'black',
                'result_bg': 'lightgray',
                'error_fg': 'red',
            },
            1: {
                'bg': 'black',
                'fg': 'white',
                'result_bg': 'darkgray',
                'error_fg': 'red',
            },
        },
    },
}


def build_css(styles):
    css = []
    outer = f'''.cls_primary_outer .cls_primary_inner {{
                    width: {styles['width']};
                    margin: {styles['margin']};
                }}
            '''
    css.append(outer)
    for theme, theme_val in styles['themes'].items():
        for dark_enabled, colors in theme_val.items():
            mode = 'dark' if dark_enabled else 'light'
            css.append(f'''.cls_theme_{theme}_{mode} {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_input {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode}
                             .cls_input.cls_error {{
                               background-color: {colors['bg']};
                               color: {colors['error_fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_result {{
                               background-color:
                                 {colors['result_bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_button {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
    css_str = ''.join(css)
    return css_str


#Css = build_css(Styles)
#flx.assets.associate_asset(__name__, 'styles.css', Css)

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
    CSS = """
    .flx-Button {
        background: #9d9;
    }       
    .flx-LineEdit {
        border: 2px solid #9d9;
    }           
    """  

    def init(self):
            super().init()
        #with flx.Widget(css_class='cls_primary_inner'):
            with flx.Widget():
                with flx.VBox():
                    with flx.FormLayout():
                        self.label = flx.Label(text='Resident Portal')
                        self.rid = \
                          flx.LineEdit(title='RID',
                                       text='')
                                       #css_class='cls_input')
                        self.submit = flx.Button(text='Submit')
                        self.status = flx.Label(text='Status: ')
        #self.base_css_class = 'cls_primary_outer'

    @flx.action
    def set_status(self, text):
        self.status.set_text(text)

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
