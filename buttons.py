from flexx import flx

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
