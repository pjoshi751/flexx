#!/usr/bin/env -S python3 -X utf8 -X dev


import flexx.flx as flx
from pscript import window


Styles = {
    'width': '40em',
    'margin': '0.5em',
    'themes': {
        'default': {
            0: {
                'bg': 'white',
                'fg': 'black',
                'result_bg': 'lightgray',
                'error_fg': 'red',
            },
            1: {
                'bg': 'black',
                'fg': 'white',
                'result_bg': 'darkgray',
                'error_fg': 'red',
            },
        },
    },
}


def latlong_to_dist_m_vincenty_js(lat1_rad, long1_rad,
                                  lat2_rad, long2_rad):

    # Vincenty formula.
    # https://en.wikipedia.org/wiki/Great-circle_distance
    #                               #Computational_formulas
    # https://en.wikipedia.org/wiki/Earth_radius
    #                               #Arithmetic_mean_radius

    Math = window.Math

    r_m = 6371008.8

    d_long_rad = long2_rad - long1_rad

    cos_lat1 = Math.cos(lat1_rad)
    sin_lat1 = Math.sin(lat1_rad)
    cos_lat2 = Math.cos(lat2_rad)
    sin_lat2 = Math.sin(lat2_rad)
    cos_d_long = Math.cos(d_long_rad)
    sin_d_long = Math.sin(d_long_rad)

    t1 = cos_lat2 * sin_d_long
    t2 = cos_lat1 * sin_lat2
    t3 = sin_lat1 * cos_lat2 * cos_d_long
    t4 = sin_lat1 * sin_lat2
    t5 = cos_lat1 * cos_lat2 * cos_d_long

    y = (t1 ** 2 + (t2 - t3) ** 2) ** 0.5
    x = t4 + t5

    central_angle_rad = Math.atan2(y, x)

    d_m = r_m * central_angle_rad

    return d_m


def str_deg_to_rad_js(s, min_deg, max_deg):
    float_pat = r'^\s*[+-]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))\s*$'
    float_re = window.RegExp(float_pat)
    if not float_re.test(s):
        return None
    deg = float(s) # Emits JS Number(s) function call.
    if window.isNaN(deg):
        return None
    if deg < min_deg or deg > max_deg:
        return None
    rad = deg * window.Math.PI / 180
    return rad


def dist_str(dist_m):
    if dist_m < 999.5:
        s = dist_m.toFixed()
        units = 'm'
    else:
        dist_km = dist_m / 1000
        units = 'km'
        n_digits = 0
        if dist_m < 100000:
            n_digits = 2
        s = dist_km.toFixed(n_digits)
    return f'{s} {units}'


def build_css(styles):
    css = []
    outer = f'''.cls_primary_outer .cls_primary_inner {{
                    width: {styles['width']};
                    margin: {styles['margin']};
                }}
            '''
    css.append(outer)
    for theme, theme_val in styles['themes'].items():
        for dark_enabled, colors in theme_val.items():
            mode = 'dark' if dark_enabled else 'light'
            css.append(f'''.cls_theme_{theme}_{mode} {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_input {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode}
                             .cls_input.cls_error {{
                               background-color: {colors['bg']};
                               color: {colors['error_fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_result {{
                               background-color:
                                 {colors['result_bg']};
                               color: {colors['fg']};
                           }}
                       ''')
            css.append(f'''.cls_theme_{theme}_{mode} .cls_button {{
                               background-color: {colors['bg']};
                               color: {colors['fg']};
                           }}
                       ''')
    css_str = ''.join(css)
    return css_str


Css = build_css(Styles)
print(Css)
flx.assets.associate_asset(__name__, 'styles.css', Css)


class LatLongDistCalculatorMain(flx.PyComponent):

    def __init__(self, *args, **kwargs):
        self.__kwargs = kwargs
        super().__init__(*args, **kwargs)

    def init(self):
        super().init()
        self.lldc = LatLongDistCalculator(**self.__kwargs)

    @flx.reaction('lldc.mode_changed')
    def handle_mode_change(self, *events):
        mode = events[-1]['mode']
        self.lldc.set_mode_status(f'Current mode: {mode}')


class LatLongDistCalculator(flx.Widget):

    def init(self):
        super().init()
        with flx.Widget(css_class='cls_primary_inner'):
            with flx.VBox():
                with flx.FormLayout():
                    self.in_lat1 = \
                      flx.LineEdit(title='Latitude 1 (deg)',
                                   text='0',
                                   css_class='cls_input')
                    self.in_long1 = \
                      flx.LineEdit(title='Longitude 1 (deg)',
                                   text='0',
                                   css_class='cls_input')
                    self.in_lat2 = \
                      flx.LineEdit(title='Latitude 2 (deg)',
                                   text='0',
                                   css_class='cls_input')
                    self.in_long2 = \
                      flx.LineEdit(title='Longitude 2 (deg)',
                                   text='0',
                                   css_class='cls_input')
                    self.lbl_distance = \
                      flx.LineEdit(title='Distance',
                                   disabled=True,
                                   text='',
                                   css_class='cls_result')
                    # Last visible form element gets cut, so using an
                    # empty label instead of Widget for flex.
                    flx.Label(text='', flex=1)
                with flx.HBox():
                    self.btn_light_mode = \
                      flx.RadioButton(text='Light mode',
                                      checked=True,
                                      css_class='cls_button')
                    self.btn_dark_mode = \
                      flx.RadioButton(text='Dark mode',
                                      css_class='cls_button')
                    flx.Widget(flex=1)
                self.lbl_mode_status = flx.Label(text='')
                flx.Widget(flex=1)
        self.base_css_class = 'cls_primary_outer'

    @flx.action
    def set_mode_status(self, text):
        self.lbl_mode_status.set_text(text)

    @flx.emitter
    def mode_changed(self, mode):
        return {'mode': mode}

    @flx.reaction('btn_light_mode.checked')
    def handle_light_mode(self, *events):
        unused = events # noqa
        if self.btn_light_mode.checked:
            css_class = self.base_css_class + \
                        ' cls_theme_default_light'
            self.set_css_class(css_class)
            self.mode_changed('light')

    @flx.reaction('btn_dark_mode.checked')
    def handle_dark_mode(self, *events):
        unused = events # noqa
        if self.btn_dark_mode.checked:
            css_class = self.base_css_class + \
                        ' cls_theme_default_dark'
            self.set_css_class(css_class)
            self.mode_changed('dark')

    @flx.reaction('in_lat1.text', 'in_long1.text',
                  'in_lat2.text', 'in_long2.text')
    def handle_latlong_change(self, *events):

        unused = events # noqa

        lat1_rad = str_deg_to_rad_js(self.in_lat1.text, -90, 90)
        cls_error = ' cls_error' if lat1_rad is None else ''
        self.in_lat1.set_css_class(f'cls_input{cls_error}')

        long1_rad = str_deg_to_rad_js(self.in_long1.text, -180, 180)
        cls_error = ' cls_error' if long1_rad is None else ''
        self.in_long1.set_css_class(f'cls_input{cls_error}')

        lat2_rad = str_deg_to_rad_js(self.in_lat2.text, -90, 90)
        cls_error = ' cls_error' if lat2_rad is None else ''
        self.in_lat2.set_css_class(f'cls_input{cls_error}')

        long2_rad = str_deg_to_rad_js(self.in_long2.text, -180, 180)
        cls_error = ' cls_error' if long2_rad is None else ''
        self.in_long2.set_css_class(f'cls_input{cls_error}')

        if None in (lat1_rad, long1_rad, lat2_rad, long2_rad):
            self.lbl_distance.set_text('')
        else:
            dist_m = \
              latlong_to_dist_m_vincenty_js(lat1_rad, long1_rad,
                                            lat2_rad, long2_rad)
            self.lbl_distance.set_text(dist_str(dist_m))


def main(argv):

    unused = argv # noqa

    '''
    with open('example.ico', 'rb') as f:
        icon_data = f.read()
    ico = flx.assets.add_shared_data('favicon.ico', icon_data)
    '''

    app = flx.App(LatLongDistCalculatorMain,
                  title='Lat Long Distance') # , icon=ico)
    # app.export('test.html', link=0)
    app.serve('')
    #app.launch('browser')
    flx.run()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
