from flexx import flx

class GridForm(flx.VBox):
    def init(self, subtitle, elements):
        super().init()
        with flx.GridLayout(ncolumns=3) as self.grid:
            flx.Label(text='', flex=(0, 0))
            flx.Label(text=subtitle, flex=(0, 0), css_class='subtitle')
            flx.Widget(flex=(1, 0))
            self.labels = []
            self.lines = []
            self.buttons = []
            self.radio = []
            self.checkbox = []
            for item in elements:
                if item[0] == 'button':
                    flx.Widget()
                    self.buttons.append(flx.Button(text=item[1]))
                    flx.Widget()
                elif item[0] == 'field':
                    self.labels.append(flx.Label(text=item[1], flex=(0, 0), css_class='col_0'))
                    self.lines.append(flx.LineEdit(text=item[2], css_class='col_1')) 
                    flx.Widget()
                elif item[0] == 'radio':
                    self.labels.append(flx.Label(text=item[1], flex=(0, 0), css_class='col_0'))
                    flx.Widget()
                    flx.Widget()
                    for radio_label in item[2]:
                        flx.Widget()
                        self.radio.append(flx.RadioButton(text=radio_label))
                        flx.Widget()
                elif item[0] == 'checkbox':
                    self.labels.append(flx.Label(text=item[1], flex=(0, 0), css_class='col_0'))
                    flx.Widget()
                    flx.Widget()
                    for radio_label in item[2]:
                        flx.Widget()
                        self.checkbox.append(flx.CheckBox(text=radio_label))
                        flx.Widget()
                   
            flx.Widget(flex=(0, 1))
            flx.Widget()
            flx.Widget()
        flx.Widget(flex=1)
