from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1.0, participation_fee=0.0)
SESSION_CONFIGS = [dict(name='public_goods_tracking', num_demo_participants=15, app_sequence=['public_goods_tracking'])]
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = ['selected_period_guessing_added']
SESSION_FIELDS = ['selected_payoff_period']
THOUSAND_SEPARATOR = ''
AUTO_TABULATE_PAYOFFS = False
ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
