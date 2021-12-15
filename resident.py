"""
Resident app
"""

from flexx import event, flx, config
from api_wrapper import get_rid_status, get_credential_types, req_otp, get_vid, update_uin, get_auth_history
from uin_update import UinUpdateForm
from buttons import MyButtons
from otp import OTPGridForm
from grid import GridForm
from vid import VidForm
from auth_lock import AuthLockForm
from auth_history import AuthHistoryForm

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
        success, status, txn_id = req_otp(uin)
        self.txn_id_map[uin] = txn_id
        self.resident.popup_window(f'Status: {status}')

    @flx.reaction('resident.vid_otp_submitted')
    def handle_otp_submitted(self, *events):
        otp = events[-1]['otp'] 
        uin = events[-1]['uin'] 
        if uin not in self.txn_id_map:
             self.resident.popup_window('Txn id not found for this UIN. Please request for OTP again')
             return 
        ok, vid, msg = get_vid(uin, self.txn_id_map[uin], otp)
        if ok:
           self.resident.clear_vid_uin() # Clear the UIN that user entered. We dont' want it be hanging around
        self.resident.popup_window(f'VID: {vid}\n\n{msg}\n\nSave the above number')

    @flx.reaction('resident.uin_update_otp_submitted')
    def handle_uin_update_otp_submitted(self, *events):
        otp = events[-1]['otp'] 
        uin = events[-1]['uin'] 
        fields = events[-1]['fields'] 
        if uin not in self.txn_id_map:
             self.resident.popup_window('Txn id not found for this UIN. Please request for OTP again')
             return 
        ok, msg = update_uin(uin, self.txn_id_map[uin], otp, fields)
        self.resident.popup_window(f'Update UIN: {msg}')

    @flx.reaction('resident.history_form_otp_submitted')
    def handle_history_form_otp_submitted(self, *events):
        otp = events[-1]['otp'] 
        uin = events[-1]['uin'] 
        nrecords = events[-1]['nrecords'] # TODO: add validation in UI for integer (although api expects str)
        if uin not in self.txn_id_map:
             self.resident.popup_window('Txn id not found for this UIN. Please request for OTP again')
             return 
        ok, history = get_auth_history(uin, self.txn_id_map[uin], otp, nrecords)
        self.resident.create_grid(history) 


class Resident(flx.Widget):

    def init(self):
        with flx.VBox():
            with flx.HBox():
                flx.Label(text='Resident HelpDesk', css_class='sitetitle')
                flx.ImageWidget(flex=1, source='https://www.omidyarnetwork.in/wp-content/uploads/2019/05/mosip.png', css_class='logo', maxsize=(120, 120))
                flx.Widget(flex=1)
            with flx.HBox():
                cls_label_selected = 'left_label_selected'
                cls_label = 'left_label'
                left_label_texts = ['RID status',
                                    'Auth lock',
                                    'Download card',
                                    'Virtual ID',
                                    'Auth history',
                                    'Update UIN',
                                   ]
                self.mybuttons = MyButtons(cls_label,
                                           cls_label_selected,
                                           left_label_texts)
                with flx.StackLayout(flex=1) as self.stack:
                    # RID status
                    self.stack_elements = []
                    w = GridForm('RID status',
                                 [('field', 'RID', ''),
                                  ('button', 'Submit'),
                                 ])
                    self.stack_elements.append(w)
                    self.rid = w.lines[0]
                    self.rid_submit = w.buttons[0]

                    # Auth lock
                    self.auth_lock = AuthLockForm()
                    self.stack_elements.append(self.auth_lock)
  
                    # eCard TODO
                    w = flx.Widget(style='background:#fff;')
                    self.stack_elements.append(w)

                    # VID
                    self.vid_form = VidForm()
                    self.stack_elements.append(self.vid_form)

                    # Auth history 
                    self.history_form = AuthHistoryForm()
                    self.stack_elements.append(self.history_form)

                    # Update UIN 
                    self.uin_form = UinUpdateForm()
                    self.stack_elements.append(self.uin_form)

            flx.Label(text='(c) MOSIP www.mosip.io', css_class='footer')

    @flx.reaction('vid_form.get_otp_submitted')
    def handle_vid_form_get_otp_submit(self, *events):
        self.uin_submitted(self.vid_form.uin.text)  # emit

    @flx.reaction('vid_form.otp_submitted')
    def handle_vid_form_otp_submit(self, *events):
        self.vid_otp_submitted(self.vid_form.uin.text, self.vid_form.otp.text)
        self.vid_form.reset_otp_form()

    @flx.reaction('uin_form.get_otp_submitted')
    def handle_uin_form_get_otp_submit(self, *events):
        self.uin_submitted(self.uin_form.uin.text)  # emit

    @flx.reaction('uin_form.otp_submitted')
    def handle_uin_form_otp_submit(self, *events):
        fields = {}
        fields['phone'] = self.uin_form.phone.text 
        fields['email'] = self.uin_form.email.text 
        fields['dob'] = self.uin_form.dob.text 
        self.uin_update_otp_submitted(self.uin_form.uin.text, self.uin_form.otp.text, fields)
        self.uin_form.reset_otp_form()

    @flx.reaction('history_form.get_otp_submitted')
    def handle_hitory_form_get_otp_submit(self, *events):
        self.uin_submitted(self.history_form.uin.text)  # emit

    @flx.reaction('history_form.otp_submitted')
    def handle_history_form_otp_submit(self, *events):
        self.history_form_otp_submitted(self.history_form.uin.text, self.history_form.otp.text, self.history_form.nrecords.text)
        self.history_form.reset_otp_form()

    @flx.reaction('auth_lock.get_otp_submitted')
    def handle_auth_lock_form_get_otp_submit(self, *events):
        self.uin_submitted(self.auth_lock.uin.text)  # emit

    @flx.reaction('auth_lock.otp_submitted')
    def handle_auth_lock_otp_submit(self, *events):
        print(self.auth_lock.checkbox)
        '''
        w = self.auth_lock
        cb1,cb2,cb3,cb4 = '','','','',''
        if w.cb1.checked:
            cb1 = w.cb1.text
        if w.cb2.checked:
            cb2 = w.cb2.text
        if w.cb3.checked:
            cb3 = w.cb3.text
        if w.cb4.checked:
            cb4 = w.cb4.text

        self.auth_lock_otp_submitted(w.uin.text, w.otp.text, w.selected_action, cb1, cb2, cb3, cb4, w.seconds.text)
        self.auth_lock.reset_otp_form()
        '''

    @flx.action
    def popup_window(self, text):
        global window
        window.alert(text)

    @flx.action
    def clear_vid_uin(self):
        self.vid_form.uin.set_text('')

    @flx.action
    def create_grid(self, history):
        self.history_form.create_grid(history)

    @flx.emitter
    def rid_submitted(self, rid):
        return {'rid': rid}

    @flx.emitter
    def uin_submitted(self, uin):
        return {'uin': uin}

    @flx.emitter
    def vid_otp_submitted(self, uin, otp):
        return {'otp': otp, 'uin': uin}

    @flx.emitter
    def uin_update_otp_submitted(self, uin, otp, fields):
        return {'uin': uin, 'otp': otp, 'fields': fields}

    @flx.emitter
    def history_form_otp_submitted(self, uin, otp, nrecords):
        return {'uin': uin, 'otp': otp, 'nrecords': nrecords}


    @flx.reaction('rid_submit.pointer_click')
    def handle_rid_submit(self, *events):
        unused = events # noqa
        self.rid_submitted(self.rid.text)

    @event.reaction('mybuttons.label_changed')
    def handle_label_change(self, *events):
        ev = events[-1]
        self.stack.set_current(self.stack_elements[ev.index])

def main(argv):

    unused = argv # noqa

    app = flx.App(ResidentMain,
                  title='Resident Portal') # , icon=ico)
    # app.export('test.html', link=0)
    #config.hostname = '0.0.0.0'
    flx.create_server(host='0.0.0.0', port=49190)
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
