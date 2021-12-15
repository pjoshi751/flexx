from flexx import flx
from otp import OTPLayout, OTPGridForm

class AuthLockForm(OTPLayout):
    def init(self):
        super().init()
        gf = OTPGridForm('Lock/unlock your authentication',
                         [('radio', 'Lock/unlock', ['lock', 'unlock']),
                          ('checkbox', 'Auth types', ['demo', 'bio-Finger', 'bio-Iris', 'bio-Face'])
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

