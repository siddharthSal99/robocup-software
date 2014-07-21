import single_robot_composite_behavior
import behavior
import skills.move
import constants
import robocup
import evaluation.window_evaluator
import main
from enum import Enum
import math


# TODO: make CompositeBehavior priorities cascade to subbehaviors of single bot behaviors


# The regular defender does a lot of calculations and figures out where it should be
# This defender lets someone else (the Defense tactic) handle calculations and blocks things based on that
class SubmissiveDefender(single_robot_composite_behavior.SingleRobotCompositeBehavior):

    class State(Enum):
        marking = 1         # gets between a particular opponent and the goal.  stays closer to the goal
        # TODO: add clear state to get and kick a free ball


    def __init__(self):
        super().__init__(continuous=True)
        self._block_object = None
        # self._opponent_avoid_threshold = 2.0
        self._defend_goal_radius = 0.9

        self.add_state(SubmissiveDefender.State.marking, behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
            SubmissiveDefender.State.marking,
            lambda: True,
            "immediately")


    def on_enter_marking(self):
        move = skills.move.Move()
        self.add_subbehavior(move, 'move', required=False) # FIXME: priority


    # move to a position to block the 'block_line'
    # if no block_line is specified, blocks the ball
    def execute_marking(self):
        move = self.subbehavior_with_name('move')
        # we move somewhere along this arc to mark our 'block_line'
        arc = robocup.Circle(robocup.Point(0,0), self._defend_goal_radius)
        # TODO: use the real shape instead of this arc approximation

        default_pt = arc.nearest_point(robocup.Point(0, constants.Field.Length / 2.0))

        target = main.ball().pos
        if self.block_line != None:
            intersects, pt1, pt2 = self.block_line.intersects_circle(arc)

            if intersects:
                # choose the pt farther from the goal
                move.pos = max([pt1, pt2], key=lambda p: p.dist_to(robocup.Point(0, 0)))
            else:
                move.pos = default_pt
        else:
            move.pos = default_pt


    def on_exit_marking(self):
        self.remove_subbehavior('move')


    # the line we should be on to block
    @property 
    def block_line(self):
        return self._block_line
    @block_line.setter
    def block_line(self, value):
        self._block_line = value


    def role_requirements(self):
        reqs = super().role_requirements()
        # FIXME: be smarter
        return reqs
