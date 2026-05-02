from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")
throttling_time = env.str("throttling_time")
domain_name = env.str("domain_name")
GROUP_CHAT_ID = env.str("GROUP_CHAT_ID")
origin = env.str("origin")

university_name_uz = env.str("university_name_uz")
university_name_ru = env.str("university_name_ru")
crm_django_domain = env.str("crm_django_domain")
username = env.str("username")
password = env.str("password")
university_id = env.int("university_id")
web_app_url = env.str("web_app_url")
port = env.int("port")
university_site_url = env.str("university_site_url")
exam_link = env.str("exam_link")
