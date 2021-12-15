from flexx import flx
from otp import OTPLayout, OTPGridForm

class AuthHistoryForm(OTPLayout):
    def init(self):
        super().init()
        gf = OTPGridForm('Fetch your Auth history',
                         [('field', 'Number of records', '10'),
                         ],
                         None
                        )
        self.uin = gf.uin
        self.get_otp = gf.get_otp
        self.otp = gf.otp
        self.otp_label = gf.otp_label
        self.submit_otp = gf.submit_otp
        self.nrecords = gf.lines[0]
        flx.Widget(flex=1)
        self.reset_otp_form()

    @flx.emitter
    def create_grid(self, history):
        return {'history': history}

    '''
    #TODO: this doesn't work
    @flx.reaction('create_grid')
    def handle_create_grid(self, *events):
        print('EVENT REACHED AUTH HISTORY')
        history = events[-1]['history']
        print(history)
        with flx.GridLayout(ncolumns=9, css_class='gridLabel'):
            for i in history:
                flx.Label(text = i)
    '''
