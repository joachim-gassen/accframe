import random

from otree.api import *

doc = """
This a is a neutral variant of experiment 1 in Evans III et al. (2001).
"""

class C(BaseConstants):
    NAME_IN_URL = 'exp3'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    COMPENSATION = 250

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pay = models.IntegerField(initial=0)
    wealth = models.IntegerField(initial = 0)
    true_amount = models.IntegerField(initial=4000)
    reported_amount = models.IntegerField(
        label="What is the amount that you want to report?"
    )
    comprehension_check1 = models.IntegerField(
        label="In each round: Who was informed about the true amount?",
        blank=False,
        choices=[
            [1, 'Only me'],
            [2, 'Me and the external party']
        ],
    )
    comprehension_check2 = models.IntegerField(
        label="Assuming that you only care about your points at the end, what would have been the optimal strategy?",
        blank=False,
        choices=[
            [1, 'Reporting 6000 points every round'],
            [2, 'Reporting the true amount every round']
        ],
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

def reported_amount_choices(player):
    return list(range(int(player.true_amount), 6050, 50))
# --- Functions ----------------------------------------------------------------

def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.true_amount = random.choice(range(4000, 6050, 50))

def set_payoffs(p):
    p.pay = p.reported_amount - p.true_amount + C.COMPENSATION
    if p.round_number > 1: 
        p.wealth = p.in_round(p.round_number - 1).wealth + \
            p.pay
    else:
        p.wealth = p.pay


# --- Pages --------------------------------------------------------------------


class Introduction(Page):
    """
    Introduction page
    """
    def is_displayed(player):
        return player.round_number == 1
    pass


class Choice(Page):
    """
    Player has to select the reported amount.
    """

    form_model = 'player'
    form_fields = ['reported_amount']

    @staticmethod
    def vars_for_template(player: Player):
        if player.round_number == 1: 
            return dict(
                true_amount=player.true_amount
            )
        if player.round_number == 2: 
            last_round_wealth = 0
        else: 
            last_round_wealth = player.in_round(player.round_number - 2).wealth
        pp = player.in_round(player.round_number - 1)
        return dict(
            last_round_wealth=last_round_wealth,
            last_round_true=pp.true_amount,
            last_round_reported=pp.reported_amount,
            last_round_diff=pp.reported_amount - pp.true_amount,
            wealth=pp.wealth,
            true_amount=player.true_amount, 
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        set_payoffs(player)



class Checks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    form_model = 'player'
    form_fields = [
        'comprehension_check1', 'comprehension_check2', 'human_check', 'feedback'
    ]

class PayoffThanks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    

page_sequence = [
    Introduction,
    Choice,
    Checks,
    PayoffThanks
]
