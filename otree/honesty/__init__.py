import random
import csv
import os

from otree.api import *

doc = """
This a is a neutral variant of experiment 1 in Evans III et al. (2001).
"""

class C(BaseConstants):
    NAME_IN_URL = 'exp3'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10
    COMPENSATION = 250
    MIN_POOL = 4000
    MAX_POOL = 6000
    STEP = 50

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pay = models.CurrencyField(initial=cu(0))
    pay_other = models.CurrencyField(initial=cu(0))
    wealth = models.CurrencyField(initial = cu(0))
    wealth_other = models.CurrencyField(initial = cu(0))
    true_amount = models.CurrencyField(initial=cu(4000))
    reported_amount = models.CurrencyField(
        label="What is the amount that you want to report?",
        blank=False
    )
    comprehension_check1 = models.IntegerField(
        label="Who was informed about the true amount?",
        blank=False,
        choices = [
            [1, 'Only me'],
            [2, 'Me and the computer of the organizers']
        ]
    )
    comprehension_check2 = models.IntegerField(
        label="Assuming that you only care about your points at the end, what would have been the optimal strategy?",
        blank=False,
        choices=[
            [1, 'Reporting 6000 points'],
            [2, 'Reporting the true amount']
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
    return list(range(int(player.true_amount), C.MAX_POOL + C.STEP, C.STEP))


# --- Functions ----------------------------------------------------------------

def creating_session(subsession: Subsession):
    use_true_amounts_from_csv = False
    if os.path.exists(__name__ + '/true_amounts.csv'):
        use_true_amounts_from_csv = True
        f = open(__name__ + '/true_amounts.csv')
        reader = list(csv.DictReader(f))

    for p in subsession.get_players():
        participant = p.participant
        if not use_true_amounts_from_csv:
            p.true_amount = random.choice(
                range(C.MIN_POOL, C.MAX_POOL + C.STEP, C.STEP)
            )
        else:
            pdata = [
                row for row in reader 
                if row['id_in_group'] == str(p.id_in_group) and 
                row['round'] == str(subsession.round_number)
            ]
            p.true_amount = pdata[0]['true_amount']
    

def set_payoffs(p):
    p.pay = p.reported_amount - p.true_amount + C.COMPENSATION
    p.pay_other = C.MAX_POOL - p.reported_amount
    if p.round_number > 1: 
        p.wealth = p.in_round(p.round_number - 1).wealth + \
            p.pay
        p.wealth_other = p.in_round(p.round_number - 1).wealth_other + \
            C.MAX_POOL - p.reported_amount
        
    else:
        p.wealth = p.pay
        p.wealth_other = C.MAX_POOL - p.reported_amount


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
            last_round_wealth_other = 0
        else: 
            last_round_wealth = player.in_round(player.round_number - 2).wealth
            last_round_wealth_other = player.in_round(player.round_number - 2).wealth_other
        pp = player.in_round(player.round_number - 1)
        return dict(
            last_round_wealth=last_round_wealth,
            last_round_wealth_other=last_round_wealth_other,
            last_round_true=pp.true_amount,
            last_round_reported=pp.reported_amount,
            last_round_diff=pp.reported_amount - pp.true_amount,
            last_round_diff_other=C.MAX_POOL - pp.reported_amount,
            wealth=pp.wealth,
            wealth_other=pp.wealth_other,
            true_amount=player.true_amount, 
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        set_payoffs(player)

class Results(Page):
    """
    Reports results.
    """
    pass


class Checks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    
    form_model = 'player'
    form_fields = [
        'comprehension_check1', 'comprehension_check2', 'human_check', 'feedback'
    ]

class Thanks(Page):
    """This page is displayed after the experimental run is complete."""
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS
    

page_sequence = [
    Introduction,
    Choice,
    Results,
    Checks,
    Thanks
]
