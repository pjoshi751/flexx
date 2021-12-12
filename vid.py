from flexx import flx
from otp import OTPLayout, OTPGridForm

class VidForm(OTPLayout):
    def init(self):
        super().init()
        '''
        with flx.FormLayout():
            self.vid_subtitle = flx.Label(text='Get VID', css_class='subtitle')
        self.populate_otp()
        '''
        gf = OTPGridForm('Get VID',
                         [
                         ],
                         None
                        )
        self.uin = gf.uin
        self.get_otp = gf.get_otp
        self.otp = gf.otp
        self.otp_label = gf.otp_label
        self.submit_otp = gf.submit_otp
        flx.Widget(flex=1)
        self.reset_otp_form()

    @flx.emitter
    def otp_submitted(self):
        v = super().otp_submitted()
        # TODO: add other relevant form fields.
        v.update({'uin': self.uin.text})
        return v
