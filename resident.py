"""
Resident app
"""

from flexx import event, flx
from api_wrapper import get_rid_status, get_credential_types, req_otp, get_vid

with open('style.css') as f:
    style = f.read()

flx.assets.associate_asset(__name__, 'style.css', style)

class ResidentMain(flx.PyComponent):

    def __init__(self, *args, **kwargs):
        self.__kwargs = kwargs
        super().__init__(*args, **kwargs)
        self.txn_id_map = {}  # uin: txn_id TODO: find an alternate way. This will keep growing.

    def init(self):
        super().init()
        self.resident = Resident(**self.__kwargs)

    @flx.reaction('resident.rid_submitted')
    def handle_rid_submitted(self, *events):
        rid = events[-1]['rid'] 
        status = get_rid_status(rid)
        self.resident.popup_window(f'Status: {status}')

    @flx.reaction('resident.uin_submitted')
    def handle_uin_submitted(self, *events):
        uin = events[-1]['uin'] 
        print(f'Event received at python uin = {uin}')
        success, status, txn_id = req_otp(uin)
        self.txn_id_map[uin] = txn_id
        self.resident.popup_window(f'Status: {status}')

    @flx.reaction('resident.otp_submitted')
    def handle_otp_submitted(self, *events):
        otp = events[-1]['otp'] 
        uin = events[-1]['uin'] 
        if uin not in self.txn_id_map:
             self.resident.popup_window('Txn id not found for this UIN. Please request for OTP again')
             return 
        ok, vid, msg = get_vid(uin, self.txn_id_map[uin], otp)
        if ok:
           self.resident.clear_vid_uin() # Clear the UIN that user entered. We dont' want it be hanging around
        self.resident.popup_window(f'VID: {vid}\n\n{msg}')


class MyButtons(flx.VBox):
    def init(self, cls_label, cls_label_selected, label_texts):
        super().init()
        self.cls_label = cls_label
        self.cls_label_selected = cls_label_selected
        self.labels = [flx.Label(text=t, css_class=self.cls_label)
                       for t in label_texts]
        flx.Widget(flex=1)  # space filler
        for i, label in enumerate(self.labels):
            label.index = i
        self.current_label = self.labels[0]
        self.current_label.set_css_class(self.cls_label_selected)

    @flx.emitter
    def label_changed(self, i):
        return {'index': i}

    @flx.reaction('labels*.pointer_down')
    def _stacked_current(self, *events):
        cur = self.current_label
        cur.set_css_class(self.cls_label)  # Reset the color
        cur  = events[-1].source  # New selected label
        cur.set_css_class(self.cls_label_selected)
        self.current_label = cur
        self.label_changed(cur.index)


class OTPLayout(flx.VBox):
    def populate_otp(self):
        with flx.StackLayout(flex=1) as self.stack:
            with flx.FormLayout() as self.get_otp_form:
                self.get_otp = flx.Button(text='Get OTP')
                flx.Widget(flex=1)
            with flx.FormLayout() as self.submit_otp_form:
                self.otp = flx.LineEdit(title='OTP', text='')
                self.submit_otp = flx.Button(text='Submit')
                flx.Widget(flex=1)

    @flx.reaction('get_otp.pointer_click')
    def handle_get_otp(self, *events):
        self.stack.set_current(self.submit_otp_form)
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
        self.stack.set_current(self.get_otp_form)


class VidForm(OTPLayout):
    def init(self):
        super().init()
        with flx.FormLayout():
            self.vid_subtitle = flx.Label(text='Get VID', css_class='subtitle')
            self.uin = flx.LineEdit(title='UIN', text='')
        self.populate_otp()
        # flx.Widget(flex=1)
    @flx.emitter
    def otp_submitted(self):
        v = super().otp_submitted()
        # TODO: add other relevant form fields.
        v.update({'uin': self.uin.text})
        return v


class Resident(flx.Widget):

    def init(self):
        with flx.VBox():
            with flx.HBox():
                flx.Label(text='Resident HelpDesk', css_class='sitetitle')
                flx.ImageWidget(flex=1, source='https://www.omidyarnetwork.in/wp-content/uploads/2019/05/mosip.png', css_class='logo')
            with flx.HBox():
                cls_label_selected = 'left_label_selected'
                cls_label = 'left_label'
                left_label_texts = ['RID status',
                                    'Auth lock',
                                    'eCard',
                                    'Virtual ID',
                                    'Virtual ID 2',
                                    'Auth history',
                                    'Update UIN',
                                   ]
                self.mybuttons = MyButtons(cls_label,
                                           cls_label_selected,
                                           left_label_texts)
                with flx.StackLayout(flex=1) as self.stack:
                    # RID status
                    self.stack_elements = []
                    with flx.FormLayout(css_class='form') as w:
                        self.stack_elements.append(w)
                        self.rid_subtitle = flx.Label(text='RID status', css_class='subtitle')
                        self.rid = flx.LineEdit(title='RID', text='')
                        self.submit = flx.Button(text='Submit')
                        flx.Widget(flex=1)

                    # Auth lock TODO
                    w = flx.Widget(style='background:#fff')
                    self.stack_elements.append(w)
  
                    # eCard TODO
                    w = flx.Widget(style='background:#fff;')
                    self.stack_elements.append(w)

                    # VID 
                    with flx.FormLayout(css_class='form') as w:
                        self.stack_elements.append(w)
                        self.vid_subtitle = flx.Label(text='Get VID', css_class='subtitle')
                        self.vid_subtitle2 = flx.Label(text='Enter your UIN number')
                        self.vid_uin = flx.LineEdit(title='UIN', text='')
                        self.vid_get_otp = flx.Button(text='Get OTP')
                        flx.Widget(flex=1, style='min-height: 50px')
                        self.vid_otp = flx.LineEdit(title='OTP', text='')
                        self.vid_submit_otp = flx.Button(text='Submit')

                    self.vid_form_2 = VidForm(css_class='form')
                    self.stack_elements.append(self.vid_form_2)

                    # Auth history TODO
                    w = flx.Widget(style='background:#fff;')
                    self.stack_elements.append(w)

                    # Update demographic info
                    with flx.FormLayout(css_class='form') as w:
                        self.stack_elements.append(w)
                        self.uin_subtitle = flx.Label(text='Update your records', css_class='subtitle')
                        flx.Label(text='')
                        self.uin_uin = flx.LineEdit(title='UIN', text='')
                        self.uin_get_otp = flx.Button(text='Get OTP')
                        flx.Label(text='')
                        self.uin_otp = flx.LineEdit(title='OTP', text='')
                        self.uin_phone = flx.LineEdit(title='Phone', text='')
                        self.uin_dob = flx.LineEdit(title='Date of Birth (YYYY/MM/DD)', text='')
                        self.uin_email = flx.LineEdit(title='Email', text='')
                        self.uin_submit = flx.Button(text='Update')
            flx.Label(text='(c) MOSIP www.mosip.io', css_class='sitefooter')

    @flx.reaction('vid_form_2.get_otp_submitted')
    def handle_vid_form_2_get_otp_submit(self, *events):
        self.uin_submitted(self.vid_form_2.uin.text)  # emit

    @flx.reaction('vid_form_2.otp_submitted')
    def handle_vid_form_2_otp_submit(self, *events):
        self.otp_submitted(self.vid_form_2.uin.text, self.vid_form_2.otp.text)
        self.vid_form_2.reset_otp_form()

    @flx.action
    def popup_window(self, text):
        global window
        window.alert(text)

    @flx.action
    def clear_vid_uin(self):
        self.vid_uin.set_text('')

    @flx.emitter
    def rid_submitted(self, rid):
        return {'rid': rid}

    @flx.emitter
    def uin_submitted(self, uin):
        return {'uin': uin}

    @flx.emitter
    def otp_submitted(self, uin, otp):
        return {'otp': otp, 'uin': uin}

    @flx.reaction('submit.pointer_click')
    def handle_rid_submit(self, *events):
        unused = events # noqa
        self.rid_submitted(self.rid.text)

    @flx.reaction('vid_get_otp.pointer_click')
    def handle_uin_submit(self, *events):
        unused = events # noqa
        self.uin_submitted(self.vid_uin.text)

    @flx.reaction('vid_submit_otp.pointer_click')
    def handle_vid_submit_otp_event(self, *events):
        unused = events # noqa
        self.vid_otp_submitted(self.vid_otp.text, self.vid_uin.text)

    @flx.reaction('uin_submit.pointer_click')
    def handle_vid_submit_otp_event(self, *events):
        unused = events # noqa

    @event.reaction('mybuttons.label_changed')
    def handle_label_change(self, *events):
        ev = events[-1]
        self.stack.set_current(self.stack_elements[ev.index])

    '''
    @event.reaction('label_a.pointer_down', 'label_b.pointer_down', 'label_c.pointer_down', 'label_d.pointer_down',
                    'label_e.pointer_down', 'label_f.pointer_down')
    def _stacked_current(self, *events):
        cur = self.current_label
        cur.set_css_class('left_label')  # Reset the color
        cur  = events[-1].source  # New selected label
        self.stack.set_current(cur.w)
        cur.set_css_class('left_label_selected')
        self.current_label = cur
    '''

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
