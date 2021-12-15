from flexx import flx
from grid import GridForm

class OTPLayout(flx.VBox):
    def populate_otp(self):
        with flx.StackLayout(flex=1) as self.stack:
            with flx.FormLayout() as self.get_otp_form:
                self.uin = flx.LineEdit(title='UIN', text='')
                self.get_otp = flx.Button(text='Get OTP')
                flx.Widget(flex=1)
            with flx.FormLayout() as self.submit_otp_form:
                self.otp = flx.LineEdit(title='OTP', text='')
                self.submit_otp = flx.Button(text='Submit')
                flx.Widget(flex=1)

    @flx.reaction('get_otp.pointer_click')
    def handle_get_otp(self, *events):
        # self.stack.set_current(self.submit_otp_form)
        self.get_otp.apply_style('visibility: hidden;')
        self.otp.apply_style('visibility: visible;')
        self.otp_label.apply_style('visibility: visible;')
        self.submit_otp.apply_style('visibility: visible;')
        self.get_otp_submitted() # emit

    @flx.reaction('submit_otp.pointer_click')
    def handle_submit_otp(self, *events):
        self.otp_submitted()

    @flx.emitter
    def otp_submitted(self):
        return {'otp': self.otp.text}

    @flx.emitter
    def get_otp_submitted(self):
        return {}

    @flx.action
    def reset_otp_form(self):
        self.otp.set_text('')
        # self.stack.set_current(self.get_otp_form)
        self.get_otp.apply_style('visibility: visible;')
        self.otp.apply_style('visibility: hidden;')
        self.otp_label.apply_style('visibility: hidden;')
        self.submit_otp.apply_style('visibility: hidden;')

class OTPGridForm(GridForm):
    def init(self, subtitle, fields):
        _fields = [('field', 'UIN', '')]
        _fields.extend(fields)
        _fields.extend([('button', 'Get OTP'),
                        ('field', 'OTP', ''),
                        ('button', 'Submit OTP'),
                       ])
        super().init(subtitle, _fields)
        self.uin = self.lines[0]
        self.get_otp = self.buttons[-2]
        self.otp = self.lines[-1]
        self.otp_label = self.labels[-1]
        self.submit_otp = self.buttons[-1]
