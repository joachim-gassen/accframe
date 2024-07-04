from otree.api import *

# This code is an adjusted variant of the oTree example code

doc = """
This is a gift exchange game that is a framed and 
simplified version of the classic
<a href="https://doi.org/10.2307/2118338" target="_blank">
    Fehr, Kirchsteiger, and Riedl (QJE, 1993)
</a>.
"""

class C(BaseConstants):
    NAME_IN_URL = 'exp8'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    WAGE_MAX = 100

cost_effort = {
    0: 0.1,
    1: 0.2,
    2: 0.3,
    4: 0.4,
    6: 0.5,
    8: 0.6,
    10: 0.7,
    12: 0.8,
    15: 0.9,
    18: 1.0
} 
effort_cost = {v: k for k, v in cost_effort.items()}   

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    wage = models.CurrencyField(
        min=cu(0),
        max=cu(100),
        doc="""Amount to send to the other participant""",
        label="What is the wage that you want to pay to the manager? Please enter a number of points from from 0 to 100:",
    )
    effort = models.FloatField(
        doc="""Multiplier to affect payoff of other participant""",
        label="Which effort level do you select? Please choose one from the table below:",
    )
    cost = models.CurrencyField()

def effort_choices(group):
    return [k for k, v in effort_cost.items() if v <= group.wage]

class Player(BasePlayer):
    wealth = models.CurrencyField(initial = cu(0))

    comprehension_check_pre1 = models.IntegerField(
        label="What is the payoff for the firm?",
        min=0,
        max=100
    )
    comprehension_check_pre2 = models.IntegerField(
        label="What is the payoff for the manager?",
        min=0,
        max=100
    )
    comprehension_check_post1 = models.IntegerField(
        label="What is the purpose of the effort level?",
        blank=False,
        choices=[
            [1, 'It is used as a multiple for the payoff of the firm'],
            [2, 'It is used as a multiple for the payoff of the manager'],
            [3, 'It is used as a multiple for the payoff of both participants']
        ],
    )
    comprehension_check_post2 = models.IntegerField(
        label="What is the effect of the cost of the effort level?",
        blank=False,
        choices=[
            [1, 'It reduces the payoff of the firm'],
            [1, 'It reduces the payoff of the manager'],
            [1, 'It reduces the payoff of both participants']
        ]
    )
    human_check = models.IntegerField(
        label="Please characterize your personality",
        blank=False,
        choices=[
            [1, 'I am a Human'],
            [2, 'I am a Bot'],
        ]
    )
    feedback = models.LongStringField(
        label="Do you have any feedback that you want to share?",
        blank=True
    )


# --- Functions ----------------------------------------------------------------

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            p.participant.wealth = cu(0)
    
def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    group.cost = effort_cost[group.effort]
    p1.payoff = int((100 - group.wage)*group.effort)
    p2.payoff = group.wage - group.cost
    p1.participant.wealth += p1.payoff
    p2.participant.wealth += p2.payoff


# --- Pages --------------------------------------------------------------------
    
class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class ComprehensionChecks(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['comprehension_check_pre1', 'comprehension_check_pre2']

class Feedback(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    def vars_for_template(player: Player):
        return dict(
            both_correct=player.comprehension_check_pre1 == 27 and 
                player.comprehension_check_pre2 == 8
        )


class Send(Page):
    """This page is only for P1"""

    form_model = 'group'
    form_fields = ['wage']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

class SendBackWaitPage(WaitPage):
    pass

class SendBack(Page):
    """This page is only for P2
    P2 sets effort level for P1"""

    form_model = 'group'
    form_fields = ['effort']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class Results(Page):
    """This page displays the earnings of each player"""

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return dict(
            wage=group.wage,
            cost=group.cost,
            effort=group.effort,
            p1_payoff=group.get_player_by_id(1).payoff,
            p2_payoff=group.get_player_by_id(2).payoff,
            p1_wealth=group.get_player_by_id(1).participant.wealth,
            p2_wealth=group.get_player_by_id(2).participant.wealth
        )

class Checks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    form_model = 'player'
    form_fields = ['comprehension_check_post1', 'comprehension_check_post2', 'human_check', 'feedback']

class Thanks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
page_sequence = [
    Introduction,
    ComprehensionChecks,
    Feedback,
    Send,
    SendBackWaitPage,
    SendBack,
    ResultsWaitPage,
    Results,
    Checks,
    Thanks
]
