from flexx import flx
from otp import OTPLayout, OTPGridForm

class UinUpdateForm(OTPLayout):
    def init(self):
        super().init()
        gf = OTPGridForm('Update your UIN details',
                         [('field', 'Phone', ''),
                          ('field', 'Email', ''),
                          ('field', 'Date of Birth (YYYY/MM/DD)', ''),
                         ],
                         None)
        self.get_otp = gf.get_otp
        self.otp = gf.otp
        self.otp_label = gf.otp_label
        self.submit_otp = gf.submit_otp
        self.phone = gf.lines[0]
        self.email = gf.lines[1]
        self.dob = gf.lines[2]
        flx.Widget(flex=1)
        self.reset_otp_form()

