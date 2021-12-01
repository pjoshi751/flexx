from flexx import flx

class Example(flx.Widget):

    CSS = """
    .flx-Button {
        background: #9d9;
    }
    """
    counter = flx.IntProp(3, settable=True)

    def init(self):
        super().init()

        with flx.HBox():
            self.but1 = flx.Button(text='reset')
            self.but2 = flx.Button(text='increase')
            self.label = flx.Label(text='', flex=1)  # take all remaining space

    @flx.action
    def increase(self):
        self._mutate_counter(self.counter + 1)

    @flx.reaction('but1.pointer_click')
    def but1_clicked(self, *events):
        self.set_counter(0)

    @flx.reaction('but2.pointer_click')
    def but2_clicked(self, *events):
        self.increase(0)

    @flx.reaction
    def update_label(self, *events):
        self.label.set_text('count is ' + str(self.counter))

app = flx.App(Example)
app.serve()
flx.run()
