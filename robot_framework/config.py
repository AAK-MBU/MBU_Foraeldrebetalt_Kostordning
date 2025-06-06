"""This module contains configuration constants used across the framework"""

# The number of times the robot retries on an error before terminating.
MAX_RETRY_COUNT = 3

# Whether the robot should be marked as failed if MAX_RETRY_COUNT is reached.
FAIL_ROBOT_ON_TOO_MANY_ERRORS = True

# Error screenshot config
SMTP_SERVER = "smtp.adm.aarhuskommune.dk"
SMTP_PORT = 25
SCREENSHOT_SENDER = "robot@friend.dk"

# Constant/Credential names
ERROR_EMAIL = "Error Email"

SERVICE_NOW_API_DEV_USER = "service_now_dev_user"
SERVICE_NOW_API_PROD_USER = "service_now_prod_user"

# Queue specific configs
# ----------------------

# The name of the job queue (if any)
QUEUE_NAME = 'bur.kostordning.main'

# The limit on how many queue elements to process
MAX_TASK_COUNT = 3000

# Miscellaneous configs
# ----------------------
FOLDER_PATH = "C:\\tmp\\Kostordning"
