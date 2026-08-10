from otree.api import *

import json
import os
import random


doc = ''


class C(BaseConstants):
    NAME_IN_URL = 'public_goods_tracking'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    NUM_PERIODS = NUM_ROUNDS // 2
    ENDOWMENT = 10
    MULTIPLIER = 1.6
    BALLS_PER_ESTIMATE = 10
    REWARD_PER_BALL = 1
    MIN_AGE = 18
    MAX_AGE = 100

    GENDER_CHOICES = [
        ['Female', 'Female'],
        ['Male', 'Male'],
        ['Non-Binary', 'Non-Binary'],
        ['Other', 'Other'],
        ['Prefer not to say', 'Prefer not to say'],
    ]
    RACE_CHOICES = [
        ['Caucasian (white)', 'Caucasian (white)'],
        ['African American', 'African American'],
        ['Latino', 'Latino'],
        ['Asian or Pacific Islander', 'Asian or Pacific Islander'],
        ['Native American', 'Native American'],
        ['Other', 'Other'],
    ]
    SEXUALITY_CHOICES = [
        ['Straight', 'Straight'],
        ['Gay', 'Gay'],
        ['Bi-Sexual', 'Bi-Sexual'],
        ['Pansexual', 'Pansexual'],
        ['Asexual', 'Asexual'],
        ['Other', 'Other'],
        ['Prefer not to say', 'Prefer not to say'],
    ]


class Subsession(BaseSubsession):
    @staticmethod
    def creating_session(subsession):
        if subsession.round_number == 1:
            subsession.session.selected_payoff_period = random.randint(1, C.NUM_PERIODS)
            subsession.group_randomly()
        elif subsession.round_number % 2 == 1:
            subsession.group_randomly()
        else:
            subsession.group_like_round(subsession.round_number - 1)

        for player in subsession.get_players():
            if subsession.round_number == 1:
                player.participant.selected_period_guessing_added = False
                set_instruction_quiz_problem(player)
            assign_target_slots(player)


class Group(BaseGroup):
    total_contribution = models.IntegerField(initial=0)
    individual_share = models.FloatField(initial=0)


class Player(BasePlayer):
    skip_instructions = models.StringField(blank=True, initial='')
    instruction_quiz_left = models.IntegerField(blank=True)
    instruction_quiz_right = models.IntegerField(blank=True)
    instruction_quiz_operator = models.StringField(blank=True)
    instruction_quiz_correct_answer = models.IntegerField(blank=True)

    instruction_quiz_answer = models.IntegerField(
        label='Your answer',
        blank=True,
    )
    photo_confirmation = models.StringField(
        choices=[['Yes', 'Yes'], ['No', 'No']],
        widget=widgets.RadioSelect,
        label='Is this you?',
        blank=True,
    )
    verified_player_number = models.IntegerField(
        label='Enter your player number',
        blank=True,
    )

    gender = models.StringField(
        choices=C.GENDER_CHOICES,
        label='What is your Gender?',
        blank=True,
    )
    race = models.StringField(
        choices=C.RACE_CHOICES,
        label='What is your Race?',
        blank=True,
    )
    ethnicity = models.StringField(
        label='Are you Hispanic or Latino?',
        blank=True,
    )
    age = models.IntegerField(
        label='What is your age?',
        min=C.MIN_AGE,
        max=C.MAX_AGE,
        blank=True,
    )
    sexuality = models.StringField(
        choices=C.SEXUALITY_CHOICES,
        label='What is your sexuality?',
        blank=True,
    )

    contribution = models.IntegerField(
        label='How many balls do you want to contribute to the public good?',
        max=C.ENDOWMENT,
        min=0,
    )
    round_payoff = models.FloatField(initial=0)
    estimation_payoff = models.IntegerField(initial=0)

    other1_target_id = models.IntegerField(blank=True)
    other2_target_id = models.IntegerField(blank=True)

    estimate_other1_json = models.LongStringField(blank=True)
    estimate_other2_json = models.LongStringField(blank=True)
    profile_guesses_json = models.LongStringField(blank=True)

    other1_gender_guess = models.StringField(
        choices=C.GENDER_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )
    other1_race_guess = models.StringField(
        choices=C.RACE_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )
    other1_ethnicity_guess = models.StringField(
        label='Guess what this player identifies as.',
        blank=True,
    )
    other1_age_guess = models.IntegerField(
        label='Guess what this player identifies as.',
        blank=True,
    )
    other1_sexuality_guess = models.StringField(
        choices=C.SEXUALITY_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )

    other2_gender_guess = models.StringField(
        choices=C.GENDER_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )
    other2_race_guess = models.StringField(
        choices=C.RACE_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )
    other2_ethnicity_guess = models.StringField(
        label='Guess what this player identifies as.',
        blank=True,
    )
    other2_age_guess = models.IntegerField(
        label='Guess what this player identifies as.',
        blank=True,
    )
    other2_sexuality_guess = models.StringField(
        choices=C.SEXUALITY_CHOICES,
        label='Guess what this player identifies as.',
        blank=True,
    )


class Estimate(ExtraModel):
    estimator = models.Link(Player)
    target_player_id = models.IntegerField()
    estimated_contribution = models.IntegerField()
    balls_placed = models.IntegerField(initial=0)
    reward_earned = models.IntegerField(initial=0)


class ProfileGuess(ExtraModel):
    guesser = models.Link(Player)
    target_player_id = models.IntegerField()
    guessed_gender = models.StringField()
    guessed_race = models.StringField()
    guessed_ethnicity = models.StringField()
    guessed_age = models.IntegerField()
    guessed_sexuality = models.StringField()


def period_number(round_number):
    return ((round_number - 1) // 2) + 1


def is_full_question_round(round_number):
    return round_number % 2 == 1


def player_image_path(player_number):
    static_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_static')
    image_dir = os.path.join(static_root, 'player_images')
    exact_name = f'Player_{player_number}.jpg'
    exact_path = os.path.join(image_dir, exact_name)
    if os.path.exists(exact_path):
        return f'player_images/{exact_name}'

    # Fallback for legacy naming variants.
    expected_stems = {f'player_{player_number}', f'player{player_number}'}
    if os.path.isdir(image_dir):
        for file_name in sorted(os.listdir(image_dir)):
            stem, _ext = os.path.splitext(file_name)
            if stem.lower() in expected_stems:
                return f'player_images/{file_name}'

    return 'player_images/Player_1.jpg'


def stable_player_number(player: Player):
    return player.participant.id_in_session


def other_players(player: Player):
    return sorted(
        [p for p in player.group.get_players() if p.id_in_subsession != player.id_in_subsession],
        key=lambda p: p.id_in_subsession,
    )


def encountered_players(player: Player):
    players_by_number = {}
    for round_number in range(1, C.NUM_ROUNDS + 1):
        round_player = player.in_round(round_number)
        for group_player in round_player.group.get_players():
            if group_player.participant == player.participant:
                continue
            player_number = stable_player_number(group_player)
            players_by_number[player_number] = group_player
    return [players_by_number[player_number] for player_number in sorted(players_by_number)]


def assign_target_slots(player: Player):
    others = other_players(player)
    player.other1_target_id = others[0].id_in_subsession if len(others) > 0 else None
    player.other2_target_id = others[1].id_in_subsession if len(others) > 1 else None


def get_target_player(player: Player, slot_number):
    others = other_players(player)
    index = slot_number - 1
    if 0 <= index < len(others):
        return others[index]
    return None


def estimate_field_name(slot_number):
    return f'estimate_other{slot_number}_json'


def make_target_context(player: Player, slot_number):
    target = get_target_player(player, slot_number)
    target_number = stable_player_number(target) if target else None
    return dict(
        slot_number=slot_number,
        target=target,
        target_id=target.id_in_subsession if target else None,
        target_number=target_number,
        target_label=f'Player {target_number}' if target else '',
        target_image=player_image_path(target_number) if target else '',
        contribution_options=list(range(C.ENDOWMENT + 1)),
        balls_per_estimate=C.BALLS_PER_ESTIMATE,
        current_period=period_number(player.round_number),
        is_full_round=is_full_question_round(player.round_number),
    )


def make_profile_question_context(player: Player, slot_number, question_field_name):
    context = make_target_context(player, slot_number)
    context['question_field_name'] = question_field_name
    context['question_prompt'] = f"Guess what {context['target_label']} identifies as."
    return context


def save_estimate_data(player: Player, slot_number):
    field_name = estimate_field_name(slot_number)
    raw_value = getattr(player, field_name)
    distribution = json.loads(raw_value)
    target = get_target_player(player, slot_number)

    for amount_str, ball_count in distribution.items():
        count = int(ball_count)
        if count <= 0:
            continue
        Estimate.create(
            estimator=player,
            target_player_id=target.id_in_subsession,
            estimated_contribution=int(amount_str),
            balls_placed=count,
        )


def save_profile_guess(player: Player, slot_number):
    target = get_target_player(player, slot_number)
    ProfileGuess.create(
        guesser=player,
        target_player_id=target.id_in_subsession,
        guessed_gender=getattr(player, f'other{slot_number}_gender_guess'),
        guessed_race=getattr(player, f'other{slot_number}_race_guess'),
        guessed_ethnicity=getattr(player, f'other{slot_number}_ethnicity_guess'),
        guessed_age=getattr(player, f'other{slot_number}_age_guess'),
        guessed_sexuality=getattr(player, f'other{slot_number}_sexuality_guess'),
    )


def save_profile_guesses_json(player: Player):
    guesses = json.loads(player.profile_guesses_json or '{}')
    for target_number_str, guess in guesses.items():
        ProfileGuess.create(
            guesser=player,
            target_player_id=int(target_number_str),
            guessed_gender=guess.get('gender', ''),
            guessed_race=guess.get('race', ''),
            guessed_ethnicity=guess.get('ethnicity', ''),
            guessed_age=int(guess.get('age')),
            guessed_sexuality=guess.get('sexuality', ''),
        )


def calculate_round_payoffs(group: Group):
    group.total_contribution = sum(p.contribution for p in group.get_players())
    total_pot = group.total_contribution * C.MULTIPLIER
    group.individual_share = total_pot / C.PLAYERS_PER_GROUP

    for player in group.get_players():
        player.round_payoff = C.ENDOWMENT - player.contribution + group.individual_share
        player.participant.payoff += cu(player.round_payoff)


def calculate_estimation_payoffs(group: Group):
    for player in group.get_players():
        total_reward = 0
        estimates = Estimate.filter(estimator=player)
        for estimate in estimates:
            target = next(
                candidate
                for candidate in group.get_players()
                if candidate.id_in_subsession == estimate.target_player_id
            )
            if estimate.estimated_contribution == target.contribution:
                reward = estimate.balls_placed * C.REWARD_PER_BALL
                estimate.reward_earned = reward
                total_reward += reward
        player.estimation_payoff = total_reward


def selected_period_guessing_payoff(player: Player):
    selected_period = player.session.selected_payoff_period
    selected_rounds = [selected_period * 2 - 1, selected_period * 2]
    return sum(player.in_round(round_number).estimation_payoff for round_number in selected_rounds)


def set_instruction_quiz_problem(player: Player):
    if player.field_maybe_none('instruction_quiz_correct_answer') is not None:
        return

    left = random.randint(10, 99)
    right = random.randint(1, 9)
    operator = random.choice(['+', '-'])
    answer = left + right if operator == '+' else left - right

    player.instruction_quiz_left = left
    player.instruction_quiz_right = right
    player.instruction_quiz_operator = operator
    player.instruction_quiz_correct_answer = answer


def is_real_experiment_session(session):
    return bool(session.config.get('is_real_experiment', True))


def instructions_skipped(player: Player):
    return bool(player.participant.vars.get('skip_instructions_and_quiz', False))


def instruction_page_is_displayed(player: Player):
    return player.round_number == 1 and not instructions_skipped(player)


def instruction_page_vars(player: Player):
    return dict(show_testing_skip=not is_real_experiment_session(player.session))


def instruction_page_before_next(player: Player, timeout_happened):
    if (
        not is_real_experiment_session(player.session)
        and player.field_maybe_none('skip_instructions') == '1'
    ):
        player.participant.vars['skip_instructions_and_quiz'] = True


class SharedInstructionsNotice(Page):
    form_model = 'player'
    form_fields = ['skip_instructions']

    @staticmethod
    def is_displayed(player: Player):
        return instruction_page_is_displayed(player)

    @staticmethod
    def vars_for_template(player: Player):
        return instruction_page_vars(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        instruction_page_before_next(player, timeout_happened)


class BaseInstructionsPage(Page):
    form_model = 'player'
    form_fields = ['skip_instructions']

    @staticmethod
    def is_displayed(player: Player):
        return instruction_page_is_displayed(player)

    @staticmethod
    def vars_for_template(player: Player):
        return instruction_page_vars(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        instruction_page_before_next(player, timeout_happened)


class Instructions(BaseInstructionsPage):
    pass


class Instructions2(BaseInstructionsPage):
    pass


class Instructions3(BaseInstructionsPage):
    pass


class Instructions4(BaseInstructionsPage):
    pass


class Instructions5(BaseInstructionsPage):
    pass


class InstructionQuiz(Page):
    form_model = 'player'
    form_fields = ['instruction_quiz_answer']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and not instructions_skipped(player)

    @staticmethod
    def vars_for_template(player: Player):
        set_instruction_quiz_problem(player)
        return dict(
            quiz_left=player.instruction_quiz_left,
            quiz_right=player.instruction_quiz_right,
            quiz_operator=player.instruction_quiz_operator,
        )

    @staticmethod
    def error_message(player: Player, values):
        set_instruction_quiz_problem(player)
        if values['instruction_quiz_answer'] != player.instruction_quiz_correct_answer:
            return 'Please answer the arithmetic question correctly before continuing.'


class PhotoVerification(Page):
    form_model = 'player'
    form_fields = ['photo_confirmation', 'verified_player_number']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and not instructions_skipped(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            player_image=player_image_path(stable_player_number(player)),
            player_number=stable_player_number(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        if values['photo_confirmation'] != 'Yes':
            return 'You must confirm your picture before continuing.'
        if values['verified_player_number'] != stable_player_number(player):
            return 'The player number must match the picture you were shown.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass


class SelfIdentification(Page):
    form_model = 'player'
    form_fields = ['age', 'ethnicity', 'race', 'gender', 'sexuality']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def error_message(player: Player, values):
        required_fields = ['age', 'ethnicity', 'race', 'gender', 'sexuality']
        for field_name in required_fields:
            value = values.get(field_name)
            if value in [None, '']:
                return 'You must answer every self-identification question before continuing.'


class ProfilePage(Page):
    form_model = 'player'
    form_fields = ['profile_guesses_json']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        targets_info = [
            dict(
                id=stable_player_number(target),
                label=f'Player {stable_player_number(target)}',
                image=player_image_path(stable_player_number(target)),
            )
            for target in encountered_players(player)
        ]
        return dict(targets_info=targets_info)

    @staticmethod
    def error_message(player: Player, values):
        targets = encountered_players(player)
        try:
            guesses = json.loads(values.get('profile_guesses_json') or '{}')
        except json.JSONDecodeError:
            return 'Your guesses could not be read. Please try again.'

        required_fields = ['age', 'ethnicity', 'race', 'gender', 'sexuality']
        for target in targets:
            target_number = str(stable_player_number(target))
            guess = guesses.get(target_number, {})
            for field_name in required_fields:
                if guess.get(field_name) in [None, '']:
                    return 'You must answer every identification question before continuing.'
            try:
                age_guess = int(guess.get('age'))
            except (TypeError, ValueError):
                return 'Age guesses must be whole numbers.'
            if age_guess < C.MIN_AGE or age_guess > C.MAX_AGE:
                return f'Age guesses must be between {C.MIN_AGE} and {C.MAX_AGE}.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        save_profile_guesses_json(player)


class Contribution(Page):
    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player):
        group_players = [
            dict(
                player_number=stable_player_number(group_player),
                image=player_image_path(stable_player_number(group_player)),
                is_self=group_player.id_in_subsession == player.id_in_subsession,
            )
            for group_player in sorted(player.group.get_players(), key=lambda p: p.id_in_subsession)
        ]
        return dict(
            group_players=group_players,
            current_period=period_number(player.round_number),
            is_full_round=is_full_question_round(player.round_number),
        )


class AfterContribution(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        calculate_round_payoffs(group)


class BaseEstimatePage(Page):
    form_model = 'player'
    slot_number = None
    template_name = 'public_goods_tracking/EstimateTarget.html'

    @classmethod
    def get_form_fields(cls, player: Player):
        return [estimate_field_name(cls.slot_number)]

    @staticmethod
    def is_displayed(player: Player):
        return True

    @classmethod
    def vars_for_template(cls, player: Player):
        context = make_target_context(player, cls.slot_number)
        context['estimate_field_name'] = estimate_field_name(cls.slot_number)
        return context

    @classmethod
    def error_message(cls, player: Player, values):
        raw_value = values[estimate_field_name(cls.slot_number)]
        if not raw_value:
            return f'You must distribute all {C.BALLS_PER_ESTIMATE} balls before continuing.'
        try:
            distribution = json.loads(raw_value)
        except json.JSONDecodeError:
            return 'Your ball distribution could not be read. Please try again.'

        total_balls = sum(int(ball_count) for ball_count in distribution.values())
        if total_balls != C.BALLS_PER_ESTIMATE:
            return f'You must distribute all {C.BALLS_PER_ESTIMATE} balls before continuing.'

    @classmethod
    def before_next_page(cls, player: Player, timeout_happened):
        save_estimate_data(player, cls.slot_number)


class EstimateOther1(BaseEstimatePage):
    slot_number = 1


class EstimateOther2(BaseEstimatePage):
    slot_number = 2


class AfterEstimation(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        calculate_estimation_payoffs(group)


class BaseProfileQuestionPage(Page):
    form_model = 'player'
    slot_number = None
    question_field = ''

    @classmethod
    def is_displayed(cls, player: Player):
        return is_full_question_round(player.round_number)

    @classmethod
    def get_form_fields(cls):
        return [f'other{cls.slot_number}_{cls.question_field}_guess']

    @classmethod
    def vars_for_template(cls, player: Player):
        context = make_target_context(player, cls.slot_number)
        context['question_field_name'] = f'other{cls.slot_number}_{cls.question_field}_guess'
        return context


class Other1Gender(Page):
    form_model = 'player'
    form_fields = ['other1_gender_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 1, 'other1_gender_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other1_gender_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other1Race(Page):
    form_model = 'player'
    form_fields = ['other1_race_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 1, 'other1_race_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other1_race_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other1Ethnicity(Page):
    form_model = 'player'
    form_fields = ['other1_ethnicity_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 1, 'other1_ethnicity_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other1_ethnicity_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other1Age(Page):
    form_model = 'player'
    form_fields = ['other1_age_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 1, 'other1_age_guess')

    @staticmethod
    def error_message(player: Player, values):
        if values.get('other1_age_guess') in [None, '']:
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other1Sexuality(Page):
    form_model = 'player'
    form_fields = ['other1_sexuality_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 1, 'other1_sexuality_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other1_sexuality_guess'):
            return 'You must answer this question before continuing.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        save_profile_guess(player, 1)

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other2Gender(Page):
    form_model = 'player'
    form_fields = ['other2_gender_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 2, 'other2_gender_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other2_gender_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other2Race(Page):
    form_model = 'player'
    form_fields = ['other2_race_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 2, 'other2_race_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other2_race_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other2Ethnicity(Page):
    form_model = 'player'
    form_fields = ['other2_ethnicity_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 2, 'other2_ethnicity_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other2_ethnicity_guess'):
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other2Age(Page):
    form_model = 'player'
    form_fields = ['other2_age_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 2, 'other2_age_guess')

    @staticmethod
    def error_message(player: Player, values):
        if values.get('other2_age_guess') in [None, '']:
            return 'You must answer this question before continuing.'

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Other2Sexuality(Page):
    form_model = 'player'
    form_fields = ['other2_sexuality_guess']

    @staticmethod
    def is_displayed(player: Player):
        return is_full_question_round(player.round_number)

    @staticmethod
    def vars_for_template(player: Player):
        return make_profile_question_context(player, 2, 'other2_sexuality_guess')

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('other2_sexuality_guess'):
            return 'You must answer this question before continuing.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        save_profile_guess(player, 2)

    template_name = 'public_goods_tracking/IdentifierQuestion.html'


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        selected_period = player.session.selected_payoff_period
        guessing_payoff = selected_period_guessing_payoff(player)
        if not getattr(player.participant, 'selected_period_guessing_added', False):
            player.participant.payoff += cu(guessing_payoff)
            player.participant.selected_period_guessing_added = True

        selected_rounds = [selected_period * 2 - 1, selected_period * 2]
        selected_round_records = [player.in_round(round_number) for round_number in selected_rounds]

        return dict(
            selected_period=selected_period,
            selected_round_records=selected_round_records,
            total_game_payoff=player.participant.payoff,
            guessing_payoff=guessing_payoff,
        )


page_sequence = [
    SharedInstructionsNotice,
    Instructions,
    Instructions2,
    Instructions3,
    Instructions4,
    Instructions5,
    InstructionQuiz,
    PhotoVerification,
    Contribution,
    AfterContribution,
    EstimateOther1,
    EstimateOther2,
    AfterEstimation,
    SelfIdentification,
    ProfilePage,
    Results,
]
