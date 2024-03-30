from otree.api import *

# This code is an adjusted variant of the oTree example code

doc = """
This is a framed gift exchange game that is a simplified version of
the classic
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
    18: 1
}    

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    wage = models.IntegerField(
        min=0,
        max=100,
        doc="""Amount received by the other participant""",
        label="How much compensation do you want to award to the manager? Please enter an amount from 0 to 100:",
    )
    cost = models.IntegerField(
        doc="""Amount sent back to the other participant""",
        label="What is the effort cost that you want to provide? Please choose a feasible amount from the list below:",
    )
    effort = models.FloatField()

def cost_choices(group):
    return list(range(0, group.wage + 1)) & cost_effort.keys()

class Player(BasePlayer):
    wealth = models.CurrencyField(initial = cu(0))

    comprehension_check_pre1 = models.IntegerField(
        label="What are the payoffs to the supervisory board?",
        min=0,
        max=100
    )
    comprehension_check_pre2 = models.IntegerField(
        label="What are the payoffs to the manager?",
        min=0,
        max=100
    )
    comprehension_check_post1 = models.IntegerField(
        label="What is the role of the effort multiple in this game?",
        blank=False,
        choices=[
            [1, 'It increases the payoff of the supervisory board'],
            [2, 'It increases the payoff of the manager'],
            [3, 'It increases the payoff of both participants']
        ],
    )
    comprehension_check_post2 = models.IntegerField(
        label="What was the effect of effort cost incured by the manager?",
        blank=False,
        choices=[
            [1, 'It directly increases the payoff of the supervisory board'],
            [2, 'It reflects the managerial effect, which in turn increases firm value and thus the payoff of the supervisory board'],
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
    
def sent_back_amount_max(group: Group):
    return group.sent_amount * C.MULTIPLIER

def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    group.effort = cost_effort[group.cost]
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
    """This page is only for P1
    P1 sends amount (all, some, or none) to P2
    This amount is tripled by experimenter,
    i.e if sent amount by P1 is 5, amount received by P2 is 15"""

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
    form_fields = ['cost']

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
