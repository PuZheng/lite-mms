# -*- coding: utf-8 -*-
from lite_sm import StateMachine, State, RuleSpecState
from lite_mms.constants import cargo as cargo_const
from lite_mms.permissions.cargo import edit_us
from lite_mms.utilities.decorators import committed

class UnloadSessionFSM(StateMachine):

    def reset_obj(self, obj):
        if obj.status == cargo_const.STATUS_LOADING:
            self.set_current_state(state_loading)
        elif obj.status == cargo_const.STATUS_WEIGHING:
            self.set_current_state(state_weighing)
        elif obj.status == cargo_const.STATUS_CLOSED:
            self.set_current_state(state_closed)

fsm = UnloadSessionFSM()

class StateLoading(RuleSpecState):
    
    @committed
    def side_effect(self):
        self.obj.status = cargo_const.STATUS_LOADING
        return self.obj.model

state_loading = StateLoading(fsm, {
    cargo_const.ACT_LOAD: (cargo_const.STATUS_WEIGHING, edit_us),
    cargo_const.ACT_CLOSE: (cargo_const.STATUS_CLOSED, edit_us)
})

class StateWeighing(RuleSpecState):

    @committed
    def side_effect(self):
        self.obj.status = cargo_const.STATUS_WEIGHING 
        return self.obj.model

state_weighing = StateWeighing(fsm, {
    cargo_const.ACT_WEIGH: (cargo_const.STATUS_LOADING, edit_us),
})

class StateClosed(RuleSpecState):

    @committed
    def side_effect(self):
        self.obj.status == cargo_const.STATUS_CLOSED
        return self.obj.model

state_closed = StateClosed(fsm, {
    cargo_const.ACT_OPEN: (cargo_const.STATUS_LOADING, edit_us)
})
