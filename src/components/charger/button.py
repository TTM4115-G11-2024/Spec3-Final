from charger import ChargerComponent
class ButtonLogic:
    def __init__(self, component: ChargerComponent):
        self.component = component
    

    def on_click(self):
        self.component.charger.stm.send("click")