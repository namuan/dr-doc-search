import logging
import os
import time
import typing
from functools import wraps

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.debug = False


def setup_logging(verbosity: int) -> None:
    logging_level = logging.WARNING
    if verbosity == 1:
        logging_level = logging.INFO
    elif verbosity >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(),
        ],
        format="%(asctime)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging_level,
    )
    logging.captureWarnings(capture=True)


def retry(
    exceptions: typing.Type[openai.error.RateLimitError], tries: int = 4, delay: int = 3, back_off: int = 2
) -> typing.Callable:
    def deco_retry(f: typing.Any) -> typing.Callable:
        @wraps(f)
        def f_retry(*args, **kwargs):  # type: ignore
            m_retries, m_delay = tries, delay
            while m_retries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = f"🚨 {e} {os.linesep} ⌛ Retrying in {m_delay} seconds..."
                    logging.warning(msg)
                    time.sleep(m_delay)
                    m_retries -= 1
                    m_delay *= back_off
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
