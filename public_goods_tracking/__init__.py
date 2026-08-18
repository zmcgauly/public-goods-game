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
    MAX_PROFILE_TARGETS = NUM_PERIODS * (PLAYERS_PER_GROUP - 1)
    ENDOWMENT = 10
    MULTIPLIER = 1.6
    BALLS_PER_ESTIMATE = 10
    REWARD_PER_BALL = 1
    POINT_DOLLAR_VALUE = 0.20
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
    SELF_RACE_CHOICES = RACE_CHOICES + [
        ['Prefer not to say', 'Prefer not to say'],
    ]
    ETHNICITY_GUESS_CHOICES = [
        ['Yes', 'Yes'],
        ['No', 'No'],
    ]
    SELF_ETHNICITY_CHOICES = ETHNICITY_GUESS_CHOICES + [
        ['Prefer not to say', 'Prefer not to say'],
    ]
    CONFIDENCE_CHOICES = [
        ['Sure', 'Sure'],
        ['Unsure', 'Unsure'],
        ['Neither sure nor unsure', 'Neither sure nor unsure'],
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
        choices=C.SELF_RACE_CHOICES,
        label='What is your Race?',
        blank=True,
    )
    ethnicity = models.StringField(
        choices=C.SELF_ETHNICITY_CHOICES,
        label='Are you Hispanic or Latino?',
        widget=widgets.RadioSelect,
        blank=True,
    )
    ethnicity_prefer_not_to_say = models.BooleanField(
        label='Prefer not to say',
        blank=True,
        initial=False,
    )
    age = models.IntegerField(
        label='What is your age?',
        min=C.MIN_AGE,
        max=C.MAX_AGE,
        blank=True,
    )
    age_prefer_not_to_say = models.BooleanField(
        label='Prefer not to say',
        blank=True,
        initial=False,
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
    gender_confidence = models.StringField(blank=True)
    guessed_race = models.StringField()
    race_confidence = models.StringField(blank=True)
    guessed_ethnicity = models.StringField()
    ethnicity_confidence = models.StringField(blank=True)
    guessed_age = models.IntegerField()
    age_confidence = models.StringField(blank=True)
    guessed_sexuality = models.StringField()
    sexuality_confidence = models.StringField(blank=True)


def period_number(round_number):
    return ((round_number - 1) // 2) + 1


def is_full_question_round(round_number):
    return round_number % 2 == 1


def player_image_path(player_number):
    static_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_static')
    image_dir = os.path.join(static_root, 'player_images')
    updated_images = {
        1: 'Player_1_20260818.jpg',
        2: 'Player_2_20260818.png',
        3: 'Player_3_20260818.png',
        4: 'Player_4_20260818.png',
        5: 'Player_5_20260818.png',
        6: 'Player_6_20260818.png',
    }
    updated_image = updated_images.get(player_number)
    if updated_image:
        return f'player_images/{updated_image}'

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


def encountered_player_for_slot(player: Player, slot_number):
    targets = encountered_players(player)
    index = slot_number - 1
    if 0 <= index < len(targets):
        return targets[index]
    return None


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


def save_profile_guesses_json(player: Player, target_number=None):
    guesses = json.loads(player.profile_guesses_json or '{}')
    for target_number_str, guess in guesses.items():
        if target_number is not None and int(target_number_str) != target_number:
            continue
        ProfileGuess.create(
            guesser=player,
            target_player_id=int(target_number_str),
            guessed_gender=guess.get('gender', ''),
            gender_confidence=guess.get('gender_confidence', ''),
            guessed_race=guess.get('race', ''),
            race_confidence=guess.get('race_confidence', ''),
            guessed_ethnicity=guess.get('ethnicity', ''),
            ethnicity_confidence=guess.get('ethnicity_confidence', ''),
            guessed_age=int(guess.get('age')),
            age_confidence=guess.get('age_confidence', ''),
            guessed_sexuality=guess.get('sexuality', ''),
            sexuality_confidence=guess.get('sexuality_confidence', ''),
        )


def calculate_round_payoffs(group: Group):
    group.total_contribution = sum(p.contribution for p in group.get_players())
    total_pot = group.total_contribution * C.MULTIPLIER
    group.individual_share = total_pot / C.PLAYERS_PER_GROUP

    for player in group.get_players():
        player.round_payoff = C.ENDOWMENT - player.contribution + group.individual_share


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


def format_dollar_amount(amount):
    return f'${amount:.2f}'


INSTRUCTION_QUIZ_QUESTIONS = [
    dict(
        question='What is your guaranteed show-up fee?',
        choices=[
            dict(text='$10', correct=True),
            dict(text='$0', correct=False),
            dict(text='$5', correct=False),
            dict(text='Only whatever I earn during the game', correct=False),
        ],
    ),
    dict(
        question='If you leave before the experiment is complete, what happens?',
        choices=[
            dict(text='I still receive the $10 show-up fee but forfeit payoff from my decisions.', correct=True),
            dict(text='I receive nothing.', correct=False),
            dict(text='I receive all possible earnings.', correct=False),
            dict(text='I must stay until the end.', correct=False),
        ],
    ),
    dict(
        question='In the main stage, who determines how much each player contributes?',
        choices=[
            dict(text='Each player chooses how much of their own endowment to contribute.', correct=True),
            dict(text='The computer chooses for everyone.', correct=False),
            dict(text='Only one group member chooses.', correct=False),
            dict(text='The experimenter chooses.', correct=False),
        ],
    ),
    dict(
        question='Which sentence correctly describes the main-stage group account payoff value?',
        choices=[
            dict(
                text='It is your endowment minus your contribution, plus your equal share of 1.6 times all group contributions.',
                correct=True,
            ),
            dict(
                text='It is only the number of balls you personally contributed to the shared account.',
                correct=False,
            ),
            dict(
                text='It is the full multiplied group total paid entirely to the player who contributed the most.',
                correct=False,
            ),
            dict(
                text='It is always 10, regardless of what anyone in the group contributes.',
                correct=False,
            ),
        ],
    ),
]


def set_instruction_quiz_problem(player: Player):
    stored_quiz = player.participant.vars.get('instruction_quiz_questions')
    if (
        player.field_maybe_none('instruction_quiz_correct_answer') is not None
        and stored_quiz
    ):
        return

    is_real_session = is_real_experiment_session(player.session)
    question_indexes = list(range(len(INSTRUCTION_QUIZ_QUESTIONS)))
    if is_real_session:
        random.shuffle(question_indexes)

    prepared_questions = []
    correct_positions = []
    for display_index, question_index in enumerate(question_indexes, start=1):
        source_question = INSTRUCTION_QUIZ_QUESTIONS[question_index]
        choices = [
            dict(position=choice_index, text=choice['text'], correct=choice['correct'])
            for choice_index, choice in enumerate(source_question['choices'], start=1)
        ]
        if is_real_session:
            random.shuffle(choices)

        for choice_position, choice in enumerate(choices, start=1):
            choice['position'] = choice_position
            if choice['correct']:
                correct_positions.append(str(choice_position))

        prepared_questions.append(
            dict(
                position=display_index,
                question=source_question['question'],
                choices=choices,
            )
        )

    player.participant.vars['instruction_quiz_questions'] = prepared_questions
    player.instruction_quiz_correct_answer = int(''.join(correct_positions))


def is_real_experiment_session(session):
    return bool(session.config.get('is_real_experiment', True))


def instructions_skipped(player: Player):
    return bool(player.participant.vars.get('skip_instructions_and_quiz', False))


def instruction_page_is_displayed(player: Player):
    return player.round_number == 1 and not instructions_skipped(player)


def instruction_page_vars(player: Player):
    return dict(
        show_testing_skip=not is_real_experiment_session(player.session),
        show_up_fee='$10',
    )


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


class DeviceInstructions(BaseInstructionsPage):
    pass


class EarningsInstructions(BaseInstructionsPage):
    pass


class RoundsInstructions(BaseInstructionsPage):
    pass


class MainStageInstructions(BaseInstructionsPage):
    pass


class ElicitationStageInstructions(BaseInstructionsPage):
    pass


class FinalInstructions(BaseInstructionsPage):
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
        quiz_questions = player.participant.vars['instruction_quiz_questions']
        return dict(
            quiz_questions=quiz_questions,
            quiz_question_count=len(quiz_questions),
        )

    @staticmethod
    def error_message(player: Player, values):
        set_instruction_quiz_problem(player)
        if values.get('instruction_quiz_answer') in [None, '']:
            return 'Please answer every quiz question before continuing.'
        if values['instruction_quiz_answer'] != player.instruction_quiz_correct_answer:
            return 'One or more quiz answers is incorrect. Please review the instructions and try again.'


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
    form_fields = [
        'age',
        'age_prefer_not_to_say',
        'ethnicity',
        'race',
        'gender',
        'sexuality',
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('age_prefer_not_to_say') and values.get('age') in [None, '']:
            return 'You must answer the age question or select prefer not to say.'

        required_fields = ['ethnicity', 'race', 'gender', 'sexuality']
        for field_name in required_fields:
            value = values.get(field_name)
            if value in [None, '']:
                return 'You must answer every self-identification question before continuing.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.age_prefer_not_to_say:
            player.age = None
        player.ethnicity_prefer_not_to_say = player.ethnicity == 'Prefer not to say'


def template_choices(choices):
    return [dict(value=value, label=label) for value, label in choices]


class BaseProfilePage(Page):
    slot_number = None
    template_name = 'public_goods_tracking/ProfilePage.html'
    form_model = 'player'
    form_fields = ['profile_guesses_json']

    @classmethod
    def is_displayed(cls, player: Player):
        return (
            player.round_number == C.NUM_ROUNDS
            and encountered_player_for_slot(player, cls.slot_number) is not None
        )

    @classmethod
    def vars_for_template(cls, player: Player):
        target = encountered_player_for_slot(player, cls.slot_number)
        target_number = stable_player_number(target)
        return dict(
            target_info=dict(
                id=target_number,
                label=f'Player {target_number}',
                image=player_image_path(target_number),
            ),
            current_target_index=cls.slot_number,
            total_targets=len(encountered_players(player)),
            gender_choices=template_choices(C.GENDER_CHOICES),
            ethnicity_choices=template_choices(C.ETHNICITY_GUESS_CHOICES),
            race_choices=template_choices(C.RACE_CHOICES),
            sexuality_choices=template_choices(C.SEXUALITY_CHOICES),
            confidence_choices=template_choices(C.CONFIDENCE_CHOICES),
        )

    @classmethod
    def error_message(cls, player: Player, values):
        target = encountered_player_for_slot(player, cls.slot_number)
        target_number = str(stable_player_number(target))
        try:
            guesses = json.loads(values.get('profile_guesses_json') or '{}')
        except json.JSONDecodeError:
            return 'Your guesses could not be read. Please try again.'

        required_fields = ['age', 'ethnicity', 'race', 'gender', 'sexuality']
        confidence_fields = [f'{field_name}_confidence' for field_name in required_fields]
        guess = guesses.get(target_number, {})
        for field_name in required_fields:
            if guess.get(field_name) in [None, '']:
                return 'You must answer every identification question before continuing.'
        for field_name in confidence_fields:
            if guess.get(field_name) in [None, '']:
                return 'You must answer how sure you are for every identification question.'

        try:
            age_guess = int(guess.get('age'))
        except (TypeError, ValueError):
            return 'Age guesses must be whole numbers.'
        if age_guess < C.MIN_AGE or age_guess > C.MAX_AGE:
            return f'Age guesses must be between {C.MIN_AGE} and {C.MAX_AGE}.'

    @classmethod
    def before_next_page(cls, player: Player, timeout_happened):
        target = encountered_player_for_slot(player, cls.slot_number)
        save_profile_guesses_json(player, stable_player_number(target))


class ProfilePage(BaseProfilePage):
    slot_number = 1


class ProfilePage2(BaseProfilePage):
    slot_number = 2


class ProfilePage3(BaseProfilePage):
    slot_number = 3


class ProfilePage4(BaseProfilePage):
    slot_number = 4


class ProfilePage5(BaseProfilePage):
    slot_number = 5


class ProfilePage6(BaseProfilePage):
    slot_number = 6


class ProfilePage7(BaseProfilePage):
    slot_number = 7


class ProfilePage8(BaseProfilePage):
    slot_number = 8


class ProfilePage9(BaseProfilePage):
    slot_number = 9


class ProfilePage10(BaseProfilePage):
    slot_number = 10


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
        guessing_payoff_points = selected_period_guessing_payoff(player)
        guessing_payoff_cash = guessing_payoff_points * C.POINT_DOLLAR_VALUE
        if not getattr(player.participant, 'selected_period_guessing_added', False):
            player.participant.payoff += cu(guessing_payoff_points)
            player.participant.selected_period_guessing_added = True

        selected_rounds = [selected_period * 2 - 1, selected_period * 2]
        selected_round_records = [player.in_round(round_number) for round_number in selected_rounds]

        return dict(
            selected_period=selected_period,
            selected_round_records=selected_round_records,
            total_game_payoff=player.participant.payoff,
            total_decision_payment_cash=format_dollar_amount(guessing_payoff_cash),
            guessing_payoff=guessing_payoff_points,
            guessing_payoff_points=guessing_payoff_points,
            guessing_payoff_cash=format_dollar_amount(guessing_payoff_cash),
            point_dollar_value=f'{C.POINT_DOLLAR_VALUE:.2f}',
        )


page_sequence = [
    SharedInstructionsNotice,
    DeviceInstructions,
    EarningsInstructions,
    RoundsInstructions,
    MainStageInstructions,
    ElicitationStageInstructions,
    FinalInstructions,
    InstructionQuiz,
    PhotoVerification,
    Contribution,
    AfterContribution,
    EstimateOther1,
    EstimateOther2,
    AfterEstimation,
    SelfIdentification,
    ProfilePage,
    ProfilePage2,
    ProfilePage3,
    ProfilePage4,
    ProfilePage5,
    ProfilePage6,
    ProfilePage7,
    ProfilePage8,
    ProfilePage9,
    ProfilePage10,
    Results,
]
