"""
Simple example that shows two forms, one which is stretched, and one
in which we use a dummy Widget to fill up space so that the form is
more compact.

This example also demonstrates how CSS can be used to apply a greenish theme.
"""

from flexx import flx, app
import requests

class Resident(app.PyComponent):

    def init(self):
        super().init()
        self.js = ThemedFormJS()

    '''
    @flx.reaction
    def get_response(self, *events):
        r = requests.get('https://www.google.com')     
        print('URL called')
    '''
         
class ThemedFormJS(flx.PyWidget):

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
        with flx.FormLayout() as self.form:
            self.b4 = flx.LineEdit(title='Name:', text='Hola')
            self.b5 = flx.LineEdit(title='Age:', text='Hello world')
            self.b6 = flx.LineEdit(title='Favorite color:', text='Foo bar')
            self.submit = flx.Button(text='Submit')
            self.label = flx.Label(text='RESPONSE')
            flx.Widget(flex=1)  # Add a spacer

    @flx.action
    def update_label(self, text):
        self.label.set_text(text)

    @flx.reaction('submit.pointer_click')
    def submit_clicked(self, *events):
        print('Hello, it works')
        r = requests.get('https://www.google.com')     
        n = len(r.content)
        print('URL called')
        self.update_label(f'{n} bytes received')

if __name__ == '__main__':
    app = flx.App(Resident)
    app.serve()
    #app.export('ThemedForm.html', link=0) 
    flx.run()
