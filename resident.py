"""
Resident app
"""

from flexx import event, flx
from api_wrapper import get_rid_status, get_credential_types, req_otp, get_vid, update_uin, get_auth_history, auth_lock

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

    @flx.reaction('resident.auth_lock_otp_submitted')
    def handle_auth_lock_otp_submitted(self, *events):
        e = events[-1]
        otp = e['otp'] 
        uin = e['uin'] 
        action = e['selected_action']
        seconds = e['seconds']
        auth_types = []
        if len(e['auth_type1']) > 0:
            auth_types.append(e['auth_type1'])
        if len(e['auth_type2']) > 0:
            auth_types.append(e['auth_type2'])
        if len(e['auth_type3']) > 0:
            auth_types.append(e['auth_type3'])
        if len(e['auth_type4']) > 0:
            auth_types.append(e['auth_type4'])

        if uin not in self.txn_id_map:
             self.resident.popup_window('Txn id not found for this UIN. Please request for OTP again')
             return 
        if action == 'Lock':
            ok = auth_lock(uin, self.txn_id_map[uin], otp, auth_types)
        elif action == 'Unlock':
            ok = auth_unlock(uin, self.txn_id_map[uin], otp, action, auth_types, seconds)
        else:
             self.resident.popup_window('Lock or Unlock not specified in user action')
             return 

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
                flx.Label(text='')
                self.get_otp = flx.Button(text='Get OTP')
                flx.Widget(flex=1)
            with flx.FormLayout() as self.submit_otp_form:
                self.otp = flx.LineEdit(title='OTP', text='')
                self.submit_otp = flx.Button(text='Submit', css_class='submit')
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

class UinUpdateForm(OTPLayout):
    def init(self):
        super().init()
        with flx.FormLayout():
            self.subtitle = flx.Label(text='Update your UIN details', css_class='subtitle')
            self.phone = flx.LineEdit(title='Phone', text='')
            self.email = flx.LineEdit(title='Email', text='')
            self.dob = flx.LineEdit(title='Date of Birth (YYYY/MM/DD)', text='')
            self.uin = flx.LineEdit(title='UIN', text='')
        self.populate_otp()

    def otp_submitted(self):
        v = super().otp_submitted()
        # TODO: add other relevant form fields.
        v.update({'uin': self.uin.text})
        return v

class AuthHistoryForm(OTPLayout):
    def init(self):
        super().init()
        with flx.FormLayout():
            self.subtitle = flx.Label(text='Fetch your Auth history', css_class='subtitle')
            self.nrecords = flx.LineEdit(title='Number of records', text='10')
            self.uin = flx.LineEdit(title='UIN', text='')
        self.populate_otp()

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

class AuthLockForm(OTPLayout):
    def init(self):
        super().init()
        self.selected_action = 'Lock'
        with flx.FormLayout():
            self.subtitle = flx.Label(text='Lock/Unlock Authentication', css_class='subtitle')
            flx.Label(text='')  # Just a gap
            with flx.VBox():
                self.subtitle = flx.Label(text='Action:', css_class='checkbox')
                self.r1 = flx.RadioButton(text='Lock', css_class='checkbox')
                self.r2 = flx.RadioButton(text='Unlock', css_class='checkbox')
            self.seconds = flx.LineEdit(title='seconds', text='86400')
            flx.Label(text='')  # Just a gap
            with flx.VBox():
                self.subtitle = flx.Label(text='Auth types:', css_class='checkbox')
                self.cb1 = flx.CheckBox(text='demo', css_class='checkbox')
                self.cb2 = flx.CheckBox(text='bio-Finger', css_class='checkbox')
                self.cb3 = flx.CheckBox(text='bio-Iris', css_class='checkbox')
                self.cb4 = flx.CheckBox(text='bio-Face', css_class='checkbox')
                flx.Label(text='')  # Just a gap
            self.uin = flx.LineEdit(title='UIN', text='')
        self.populate_otp()

    @flx.reaction('r1.checked', 'r2.checked')
    def handle_radio_changed(self):
        ev = events[-1]
        self.selected_action = ev.source.text
    
class Resident(flx.Widget):
    def init(self):
        with flx.VBox():
            with flx.HBox():
                flx.Label(text='Resident HelpDesk', css_class='sitetitle')
                flx.ImageWidget(flex=1,source='https://www.omidyarnetwork.in/wp-content/uploads/2019/05/mosip.png', css_class='logo')
            with flx.HBox():
                cls_label_selected = 'left_label_selected'
                cls_label = 'left_label'
                left_label_texts = ['RID status',
                                    'Auth lock',
                                    'eCard',
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
                    with flx.FormLayout(css_class='form') as w:
                        self.stack_elements.append(w)
                        self.rid_subtitle = flx.Label(text='RID status', css_class='subtitle')
                        flx.Label(title='', text='')
                        self.rid = flx.LineEdit(title='RID', text='')
                        flx.Label(title='', text='')
                        self.rid_submit = flx.Button(text='Submit', css_class='submit')
                        flx.Widget(flex=1)

                    # Auth lock
                    self.auth_lock = AuthLockForm(css_class='form')
                    self.stack_elements.append(self.auth_lock)
  
                    # eCard TODO
                    w = flx.Widget(style='background:#fff;')
                    self.stack_elements.append(w)

                    # VID
                    self.vid_form = VidForm(css_class='form')
                    self.stack_elements.append(self.vid_form)

                    # Auth history 
                    self.history_form = AuthHistoryForm(css_class='form')
                    self.stack_elements.append(self.history_form)

                    # Update UIN 
                    self.uin_form = UinUpdateForm(css_class='form')
                    self.stack_elements.append(self.uin_form)

            flx.Label(text='(c) MOSIP www.mosip.io', css_class='sitefooter')

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
    def handle_history_form_get_otp_submit(self, *events):
        self.uin_submitted(self.history_form.uin.text)  # emit

    @flx.reaction('history_form.otp_submitted')
    def handle_history_form_otp_submit(self, *events):
        self.history_form_otp_submitted(self.history_form.uin.text, self.history_form.otp.text, self.history_form.nrecords.text)
        self.history_form.reset_otp_form()

    @flx.reaction('auth_lock.get_otp_submitted')
    def handle_auth_lock_get_otp_submit(self, *events):
        self.uin_submitted(self.auth_lock.uin.text)  # emit

    @flx.reaction('auth_lock.otp_submitted')
    def handle_auth_lock_otp_submit(self, *events):
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

    @flx.emitter
    def auth_lock_otp_submitted(self, uin, otp, action, cb1, cb2, cb3, cb4, seconds):
        return {'uin': uin, 'otp': otp, 'selected_action': action, 'auth_type1': cb1, 'auth_type2': cb2, 
                'auth_type3': cb3, 'auth_type4': cb4, 'seconds': seconds}

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
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
