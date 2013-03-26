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
        self.obj = obj

fsm = UnloadSessionFSM()

class StateLoading(RuleSpecState):
    status = cargo_const.STATUS_LOADING
    
    @committed
    def side_effect(self):
        self.obj.status = cargo_const.STATUS_LOADING
        return self.obj.model

state_loading = StateLoading(fsm, {
    cargo_const.ACT_LOAD: (cargo_const.STATUS_WEIGHING, edit_us),
    cargo_const.ACT_CLOSE: (cargo_const.STATUS_CLOSED, edit_us)
})

class StateWeighing(State):
    status = cargo_const.STATUS_WEIGHING

    @committed
    def side_effect(self):
        self.obj.status = cargo_const.STATUS_WEIGHING 
        return self.obj.model

    def next(self, action):
        edit_us.test()
        if action == cargo_const.ACT_WEIGH:
            if any(task.is_last for task in self.obj.task_list):
                return state_closed
            return state_loading

state_weighing = StateWeighing(fsm)

class StateClosed(RuleSpecState):
    status = cargo_const.STATUS_CLOSED

    @committed
    def side_effect(self):
        self.obj.status == cargo_const.STATUS_CLOSED
        return self.obj.model

state_closed = StateClosed(fsm, {
    cargo_const.ACT_OPEN: (cargo_const.STATUS_LOADING, edit_us)
})

