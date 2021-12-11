"""
Resident app
"""

from flexx import event, flx, config
from api_wrapper import get_rid_status, get_credential_types, req_otp, get_vid, update_uin, get_auth_history

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
            for item in elements:
                if item[0] == 'button':
                    flx.Widget()
                    self.buttons.append(flx.Button(text=item[1]))
                    flx.Widget()
                elif item[0] == 'field':
                    self.labels.append(flx.Label(text=item[1], flex=(0, 0), css_class='col_0'))
                    self.lines.append(flx.LineEdit(text=item[2], css_class='col_1')) 
                    flx.Widget()
            flx.Widget(flex=(0, 1))
            flx.Widget()
            flx.Widget()
        flx.Widget(flex=1)


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

                    # Auth lock TODO
                    w = flx.Widget(style='background:#fff')
                    self.stack_elements.append(w)
  
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
    def handle_hitory_form_get_otp_submit(self, *events):
        self.uin_submitted(self.history_form.uin.text)  # emit

    @flx.reaction('history_form.otp_submitted')
    def handle_history_form_otp_submit(self, *events):
        self.history_form_otp_submitted(self.history_form.uin.text, self.history_form.otp.text, self.history_form.nrecords.text)
        self.history_form.reset_otp_form()

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
    config.hostname = '0.0.0.0'
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
